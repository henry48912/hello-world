import sys
import time
from datetime import datetime

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
    msg['Subject'] = "LMP Message"
    msg.attach(MIMEText(str(msgText), "plain"))
    text = msg.as_string()

    SSL_context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=SSL_context)
        server.login(sender, sender_password)
        server.sendmail(sender, recipient, text)


def login(account):

    import undetected_chromedriver

    driver = undetected_chromedriver.Chrome()
    driver.get(account[0][5])
    driver.maximize_window()

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='hs_cos_wrapper_widget_1621856686244']/div/div/div/div/div[2]/form/input[1]")
            button.clear()
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//*[@id='hs_cos_wrapper_widget_1621856686244']/div/div/div/div/div[2]/form/input[2]")
            button.clear()
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "//*[@id='hs_cos_wrapper_widget_1621856686244']/div/div/div/div/div[2]/form/input[3]")
            button.click()
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("IndependentBank: Unable to login for 30 seconds")
                sys.exit()

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='M_layout_content_PCDZ_M4HNZU6_ctl00_webInputForm_btnSave']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("IndependentBank: Unable to get main page info for 30 seconds")
                sys.exit()
    button.click()

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"M_layout_content_PCDZ_MB4PY2_ctl00_Accounts"})
            data = response[0].contents[1].contents[1].contents
            AcctNumber = account[0][1]
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("IndependentBank: Unable to get balance info for 30 seconds")
                sys.exit()

    WriteData(data, datetime.now(), AcctNumber)
    GetTransactions(driver, AcctNumber)

    driver.close()


def GetTransactions(driver, AcctNumber):

    from bs4 import BeautifulSoup

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            driver.get('https://independentbank.onlinebank.com/Accounts/AccountActivity.aspx')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"M_layout_content_PCDZ_M2SN6LC_ctl00_transactionsGrid"})
            data = response[0].contents[1].contents
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("IndependentBank: Unable to load transactions page for 30 seconds")
                sys.exit()

    for iTrans in range(1, len(data)-1):
        TransDateStr = response[0].contents[1].contents[iTrans].contents[1].text
        TransDate = datetime.strptime(TransDateStr, '%m/%d/%Y')
        Description = response[0].contents[1].contents[iTrans].contents[2].text
        Amount = "-" + response[0].contents[1].contents[iTrans].contents[3].text
        TransType = "Health"
        if Amount == " ":
            Amount = response[0].contents[1].contents[iTrans].contents[4].text
            TransType = "Interest"
        Amount = Amount.replace('$', '').replace(',', '')
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

    FundName = response[1].text
    Shares = response[3].text.strip('$')
    datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','Cash','" +  FundName + "','" + Shares.replace(',', '') + "','1'")

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
    SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='IndependentBank' ORDER BY Account_Name, Account_Username"
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