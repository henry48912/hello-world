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
            button = driver.find_element(By.XPATH, "//*[@id='userId']")
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//*[@id='password']")
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "/html/body/app-root/div/crs-core/div/signon-layout/div/section[2]/section/section[2]/section/sign-on-form/section/div[1]/div[1]/div/form/button")
            button.click()
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Meijer: Unable to login for 30 seconds")
                sys.exit()

    return driver
    
def ReadData(account):

    driver = login(account)

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            tempStr = driver.find_element(By.XPATH, "//*[@id='maincontent']/section[2]/section[1]/article[1]/div[1]/dl[2]/dd[1]").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Meijer: Unable to get account info for 30 seconds")
                sys.exit()

    data = tempStr.replace(',','').strip('$')
    AcctNumber = account[0][1]

    WriteData(data, datetime.now(), AcctNumber)

    GetTransactions(driver, AcctNumber)

    driver.close()


def GetTransactions(driver, AcctNumber):

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table")

    for i in range(6, len(response[0].contents)):
        tempStr = response[0].contents[i].text.split('\n')
        stripStr = []
        for j in range(0, len(tempStr)):
            if tempStr[j].strip() != '':
                stripStr.append(tempStr[j].lstrip())

        if len(stripStr) == 0:
            break

        for j in range(0, len(stripStr)):
            if stripStr[j].startswith("TYPE"):
                trans_type = stripStr[j][4:]
                amtStr = stripStr[j-1]

        WriteYear = datetime.now().year
        if datetime.now().month < 3 and stripStr[0][:3] != "Dec":
            WriteYear = WriteYear - 1
        trans_dateStr = stripStr[0] + ", " + str(WriteYear)
        trans_date = datetime.strptime(trans_dateStr, '%b %d, %Y')
        descStr = stripStr[1].replace("'", ' ')
        trans_amount = amtStr.replace('$','').replace(',','')
        if trans_type == "interest charged" or trans_type == "sale":
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
    
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + descStr + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)

    time.sleep(5)
    dropdown = driver.find_element(By.XPATH, "//*[@id='maincontent']/section[3]/section[2]/section[1]/form/div[1]/div/div/select")
    dropdown.click()
    dropdown.send_keys(Keys.DOWN)
    dropdown.send_keys(Keys.RETURN)

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table")
            data = response[0].contents
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Meijer: Unable to get prior month transactions for 30 seconds")
                sys.exit()

    for i in range(6, len(response[0].contents)):
        tempStr = response[0].contents[i].text.split('\n')
        stripStr = []
        for j in range(0, len(tempStr)):
            if tempStr[j].strip() != '':
                stripStr.append(tempStr[j].lstrip())

        if len(stripStr) == 0:
            break
        
        for j in range(0, len(stripStr)):
            if stripStr[j].startswith("TYPE"):
                trans_type = stripStr[j][4:]
                amtStr = stripStr[j-1]

        WriteYear = datetime.now().year
        if datetime.now().month < 3 and stripStr[0][:3] != "Dec":
            WriteYear = WriteYear - 1
        trans_dateStr = stripStr[0] + ", " + str(WriteYear)
        trans_date = datetime.strptime(trans_dateStr, '%b %d, %Y')
        descStr = stripStr[1].replace("'", ' ')
        trans_amount = amtStr.replace('$','').replace(',','')
        if trans_type == "interest charged" or trans_type == "sale":
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
    
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + descStr + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)


def WriteTrans(dataStr):

    import sys

    import mysql.connector

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "INSERT INTO Financial.Transactions VALUES (" + dataStr + ")"
        cursor.execute(SQLStmt)
        conn1.commit()
    except:
        if sys.exc_info()[1].msg[:15] == "Duplicate entry":
            print("Duplicate Entry")
        else:
            print(sys.exc_info())
            print(dataStr)

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

    datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','Credit','Card Balance','" + response.replace(',', '') + "','1'")

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



if __name__ == '__main__':

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='Meijer' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)