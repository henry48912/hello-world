import sys
import time
from datetime import datetime

import mysql.connector
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
            button = driver.find_element(By.XPATH, "//input[@name='username']")
            button.clear()
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//input[@name='password']")
            button.clear()
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "//input[@id='loginSubmitBtn']")
            button.click()
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("BWL: Unable to login for 30 seconds")
                sys.exit()

    return driver


def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)

    driver.get('https://www.mybwlretirement.com/iApp/rsc/fundDetailsView.x')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//h1[@id='page-title']/span")
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"investmentBalanceTablebyFund"})
            AcctNumber = account[0][1]
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("BWL: Unable to load funds page for 30 seconds")
                sys.exit()

    WriteData(response, datetime.now(), AcctNumber)
    GetTransactions(driver, AcctNumber)

    driver.close()


def GetTransactions(driver, AcctNumber):

    from bs4 import BeautifulSoup

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            driver.get('https://www.mybwlretirement.com/iApp/rsc/transHistorySummary.x')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"transSummary"})
            StartMonth = datetime.now().month - 1
            StartYear = datetime.now().year
            if StartMonth == 0: 
                StartMonth = 12
                StartYear = StartYear - 1
            StartDateStr = str(StartMonth) + "/1/" + str(StartYear)
            StartDate = datetime.strptime(StartDateStr, '%m/%d/%Y')
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("BWL: Unable to load funds page for 30 seconds")
                sys.exit()

    for iTrans in range(0, len(response[0].contents[4].contents)):
        TransInfo = response[0].contents[4].contents[iTrans].text.split('\n')
        TransDateStr = TransInfo[1]
        TransDate = datetime.strptime(TransDateStr, '%m/%d/%Y')
        if TransDate >= StartDate:
            button = driver.find_element(By.XPATH, "//*[@id='transSummary']/tbody/tr[" + str(iTrans+1) + "]/td[2]/a")
            button.click()
            tryloop = True
            counter = 0
            while tryloop == True:
                try:
                    GetTransData(driver, TransDate, AcctNumber)
                    break
                except:
                    time.sleep(1)
                    counter = counter + 1
                    if counter == 30:
                        SendEmail("BWL: Unable to load transactions page for 30 seconds")
                        sys.exit()
        else:
            break
        button = driver.find_element(By.XPATH, "//*[@id='content']/p/a")
        button.click()

def GetTransData(driver, TransDate, AcctNumber):

    from bs4 import BeautifulSoup

    TransType = driver.find_element(By.XPATH, "//*[@id='content']/div[4]/strong").text
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table", {"id":"t2679"})

    for iTrans in range(1, len(response[0].contents[3].contents), 2):
        TransInfo = response[0].contents[3].contents[iTrans].text.split('\n')
        Description = TransInfo[1] + ": Shares, " + TransInfo[2]
        Amount = TransInfo[4].replace('$', '').replace(',', '')
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

    for item in response:
        NumberOfFunds = len(item.contents[4].contents)
        for i in range(1,NumberOfFunds):
            TextStr = item.contents[4].contents[i].contents[1].text
            FundName = TextStr[:TextStr.find("\n")]
            Ticker = TextStr[TextStr.find('Ticker: ')+8:]
            Ticker = Ticker[:Ticker.find('\n')]
            Shares = item.contents[4].contents[i].contents[5].text
            Price = item.contents[4].contents[i].contents[7].text
            datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','"  + Ticker + "','" +  FundName + "','" + Shares.replace(',', '') + "','" + Price + "'")

            try:
                SQLStmt = "INSERT INTO Financial.Funds VALUES (" + datarow + ")"
                cursor.execute(SQLStmt)
                conn1.commit()
            except:
                if sys.exc_info()[1].msg[:15] == "Duplicate entry":
                    print("Duplicate Entry")

    cursor.close()
    conn1.close()


conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

try:
    cursor = conn1.cursor()
except:
    print(sys.exc_info())

try:
    SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='BWL' AND Account_Type='Investment' ORDER BY Account_Name, Account_Username"
    cursor.execute(SQLStmt)
    Accounts = list(cursor.fetchall())
except:
    if sys.exc_info()[1].msg[:13] == "Duplicate entry":
        print("Duplicate Entry")

cursor.close()
conn1.close()

ReadData(Accounts)
