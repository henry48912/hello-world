import sys
import time
from datetime import datetime
import undetected_chromedriver as uc

import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def SendEmail(msgText):

    import smtplib
    import ssl
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    port = 587  
    smtp_server = "smtp-mail.outlook.com"
    sender = "brent.henry@outlook.com"
    recipient = "brent.henry@outlook.com"
    sender_password = "HelloKitty2"
    msg = MIMEMultipart()

    msg['From'] = "brent.henry@outlook.com"
    msg['To'] = "brent.henry@outlook.com"
    msg['Subject'] = "Financial Message"
    msg.attach(MIMEText(str(msgText), "plain"))
    text = msg.as_string()

    SSL_context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=SSL_context)
        server.login(sender, sender_password)
        server.sendmail(sender, recipient, text)


def login(account):


    chrome_options = uc.ChromeOptions()
    userdatadir='/home/brent/Documents/Applications/Financial/~/Documents/Brent/Profile 1'
    userprofiledir='/home/brent/.config/google-chrome/Brent'
    chrome_options.add_argument("--user-data-directory={userdatadir}")
    chrome_options.add_argument("--profile-directory={userprofiledir}")
    chrome_options.add_argument("--start-maximized")

    driver = uc.Chrome(options=chrome_options)
    driver.get(account[0][5])
    driver.maximize_window()

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_txtUserIdStandard']")
            button.clear()
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_txtPassword']")
            button.clear()
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "//*[@id='ctl00_modulePageContent_btnLogin']")
            button.click()
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("HealthEquity: Unable to login for 30 seconds")
                sys.exit()

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            driver.get('https://my.healthequity.com/Member/AccountSummary.aspx?')
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("HealthEquity: Unable to get main page info for 30 seconds")
                sys.exit()

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            Balance = driver.find_element(By.XPATH, "//*[@id='bodyContent-main']/span/div/div[1]/div/div/ul/li[1]/span[2]/span[1]").text
            AcctNumber = account[0][1]
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("HealthEquity: Unable to get balance info for 30 seconds")
                sys.exit()

    WriteData(Balance, datetime.now(), AcctNumber)
    GetTransactions(driver, AcctNumber)

    driver.close()


def GetTransactions(driver, AcctNumber):

    from bs4 import BeautifulSoup

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            driver.get('https://my.healthequity.com/Member/MemberTransactions.aspx?Subaccount=HSA&MemberId=22715410')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"ctl00_modulePageContent_MemberTransactionsStyled_gvTransferLines"})
            data = response[0].contents[1].contents
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("IndependentBank: Unable to load transactions page for 30 seconds")
                sys.exit()

    for iTrans in range(1, len(data)-1):
        TransDateStr = response[0].contents[1].contents[iTrans].contents[1].text.replace('\n','').replace(' ','')
        TransDate = datetime.strptime(TransDateStr, '%m/%d/%Y')
        Description = response[0].contents[1].contents[iTrans].contents[2].text
        Description = Description[Description.find('\n')+1:].strip(' ')
        Description = Description[:Description.find('\n')]
        Amount = response[0].contents[1].contents[iTrans].contents[3].text.replace('\n','')
        TransType = "Health"
        Amount = Amount.replace('$', '').replace(',', '')
        if Amount[0] == "(":
            Amount = "-" + Amount[1:len(Amount)-1]
        if float(Amount) > 0:
            if Description.startswith('Interest'):
                TransType = 'Interest'
            if Description.startswith('Employee Contribution'):
                TransType = 'Contribution'
            if Description.startswith('Balance Forward'):
                break
        transStr = "'" + TransDate.strftime('%Y-%m-%d') + "','" + AcctNumber + "','" + Description + "','" + TransType + "','" + Amount + "'"

        WriteTransData(transStr)



def WriteTransData(transdata):

    import sys

    import mysql.connector

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "INSERT INTO Financial.Transactions VALUES (" + transdata + ")"
        cursor.execute(SQLStmt)
        conn1.commit()
    except:
        if sys.exc_info()[1].msg[:15] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()



def WriteData(response, dateStr, AcctNumber):

    import sys

    import mysql.connector

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    Shares = response.replace('$','')
    datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','Cash','Cash','" + Shares.replace(',', '') + "','1'")

    try:
        SQLStmt = "INSERT INTO Financial.Funds VALUES (" + datarow + ")"
        cursor.execute(SQLStmt)
        conn1.commit()
    except:
        if sys.exc_info()[1].msg[:15] == "Duplicate entry":
            print("Duplicate Entry")
        else:
            print(sys.exc_info())
            print(SQLStmt)

    cursor.close()
    conn1.close()



conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

try:
    cursor = conn1.cursor()
except:
    print(sys.exc_info())

try:
    SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='HealthEquity' ORDER BY Account_Name, Account_Username"
    cursor.execute(SQLStmt)
    Accounts = list(cursor.fetchall())
except:
    if sys.exc_info()[1].msg[:13] == "Duplicate entry":
        print("Duplicate Entry")
    else:
        print(sys.exc_info())
        print(SQLStmt)

cursor.close()
conn1.close()

ReadData(Accounts)