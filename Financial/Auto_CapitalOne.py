import sys
import time
from datetime import datetime, timedelta

import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By


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


def ReadData(Accounts):

    import asyncio
    import sys
    import time

    from bs4 import BeautifulSoup
    from pyppeteer import launch

    async def CapitalOne():

        FundData = []

        browser = await launch(headless=False, executablePath='/usr/bin/google-chrome', userDataDir="/home/brent/Documents/")
        page = await browser.newPage()
        await page.setViewport({'width': 1920, 'height': 1080})
        await page.goto(Accounts[0][5])
        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                userid = await page.waitForXPath("//*[@id='ods-input-0']")
                await userid.type(Accounts[0][3])
                pword = await page.waitForXPath("//*[@id='ods-input-1']")
                await pword.type(Accounts[0][4])
                button = await page.waitForXPath("/html/body/app-root/div/div/app-sign-in/ci-content-card/div/div/ngx-ent-signin/form/p[2]/button")
                await button.click()
                element = await page.waitForXPath("//*[@id='number_...3907']")
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("CapitalOne: Unable to login for 30 seconds")
                    sys.exit()

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                page_text = await page.content()
                soup = BeautifulSoup(page_text, 'html.parser')
                response = soup.find(id="page-content")
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("CapitalOne: Unable to access main page for 30 seconds")
                    sys.exit()

        tempStr = response.contents[1].text.split("ending in")
        for acct in range(1,5):
            if tempStr[acct][4:8] == Accounts[0][1][len(Accounts[0][1])-4:]:
                Quantity = tempStr[acct][tempStr[acct].find("AVAILABLE BALANCE")+20:]
                Quantity = Quantity[:Quantity.find("AVAILABLE BALANCE")]
                FundData.append(Accounts[0][1] + ',,Cash,1,' + Quantity.replace(',',''))
                searchaccount = "'number_" + tempStr[acct][1:8] + "'"
                element = await page.waitForXPath("//*[@id=" + searchaccount + "]")
                await element.click()

                tryloop = True
                counter = 0
                while tryloop == True:
                    try:
                        page_text = await page.content()
                        soup = BeautifulSoup(page_text, 'html.parser')
                        response = soup.find("c1-ease-table")
                        data = response.text
                        break
                    except:
                        time.sleep(1)
                        counter = counter + 1
                        if counter == 30:
                            SendEmail("CapitalOne: Unable to access account transactions page for 30 seconds")
                            sys.exit()

                WriteTransactions(data, Accounts[0][1])
                element = await page.waitForXPath("//*[@id='header__back-button__content']")
                await element.click()
                time.sleep(5)
                break

        for acct in range(1,5):
            if tempStr[acct][4:8] == Accounts[1][1][len(Accounts[1][1])-4:]:
                Quantity = tempStr[acct][tempStr[acct].find("AVAILABLE BALANCE")+20:]
                Quantity = Quantity[:Quantity.find("AVAILABLE BALANCE")]
                FundData.append(Accounts[1][1] + ',,Cash,1,' + Quantity.replace(',',''))
                searchaccount = "'number_" + tempStr[acct][1:8] + "'"
                element = await page.waitForXPath("//*[@id=" + searchaccount + "]")
                await element.click()

                tryloop = True
                counter = 0
                while tryloop == True:
                    try:
                        page_text = await page.content()
                        soup = BeautifulSoup(page_text, 'html.parser')
                        response = soup.find("c1-ease-table")
                        data = response.text
                        break
                    except:
                        time.sleep(1)
                        counter = counter + 1
                        if counter == 30:
                            SendEmail("CapitalOne: Unable to access account transactions page for 30 seconds")
                            sys.exit()

                WriteTransactions(data, Accounts[1][1])
                element = await page.waitForXPath("//*[@id='header__back-button__content']")
                await element.click()
                time.sleep(5)
                break

        WriteData(FundData, datetime.now())
        await browser.close()

    asyncio.get_event_loop().run_until_complete(CapitalOne())



def WriteTransactions(data, AcctNumber):
    
    import sys
    from datetime import datetime

    import mysql.connector

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    CurrentMonth = datetime.now().strftime('%b')
    if CurrentMonth == "Jan":
        LastDateStr = "12/1/" + str(datetime.now().year-1)
    else:
        LastDateStr = str(datetime.now().month-1) + "/1/" + str(datetime.now().year)
    LastMonth = datetime.strptime(LastDateStr, '%m/%d/%Y').strftime('%b')

    while data != "":

        tdata = data[:data.find("$")]
        if tdata == "": 
            data = ""
            break

        s_loc = data.find(CurrentMonth)
        if s_loc == -1:
            s_loc = data.find(LastMonth)
            if s_loc == -1:
                break
        temp_loc = data.find('$') + 1
        temp_str = data[data.find('$') + 1:]
        e_loc = temp_str.find('$') + temp_loc - 1
        transaction = data[s_loc:e_loc]
        data = data[e_loc+2:]
        trans_data = transaction.split(' ')
        trans_month = trans_data[0]
        trans_day = trans_data[2]
        trans_year = str(datetime.now().year)
        if trans_month == "Dec": trans_year = str(datetime.now().year - 1)
        dateStr = trans_month + " " + trans_day + ", " + trans_year
        datefmt = datetime.strptime(dateStr, '%b %d, %Y')
        trans_amount = trans_data[len(trans_data)-2]
        trans_amount = trans_amount.replace(',','').replace('$','')
        trans_type = trans_data[len(trans_data)-3]
        trans_desc = trans_data[3]
        for inc in range(4,len(trans_data)-3):
            trans_desc = trans_desc + " " + trans_data[inc]

        if trans_type == "Transfer":
            if trans_desc == "MI DIR ACH Transfer":
                trans_type = "Other Expenses"
            if trans_desc == "CONSUMERS ENERGY Transfer":
                trans_type = "Utilities"
            if trans_desc == "VENMO Transfer":
                trans_type = "Misc"
            if trans_desc == "STATE OF MICH Transfer":
                trans_type = "Misc"
            if trans_desc == "NORDSTROM Transfer":
                trans_type = "Clothing"
        if trans_type == "Payment":
            if trans_desc.startswith("Check #"):
                trans_type = "Misc"
            if trans_desc.startswith("Chase Home Finance"):
                trans_type = "Mortgage"
            if trans_desc == "DEWITT CHARTER TOWNSHIP Bill Payment Bill":
                if float(trans_amount) < -500:
                    trans_type = "TAXES"
                else:
                    trans_type = "Utilities"
    
        datarow = "'" + datefmt.strftime('%Y-%m-%d') + "','" + AcctNumber + "','" + trans_desc + "','" + trans_type + "','" + trans_amount.replace('$','') + "'"

        try:
            SQLStmt = "INSERT INTO Financial.Transactions VALUES (" + datarow + ")"
            cursor.execute(SQLStmt)
            conn1.commit()
        except:
            if sys.exc_info()[1].msg[:15] == "Duplicate entry":
                print("Duplicate Entry")

    cursor.close()
    conn1.close()



def WriteData(response, dateStr):

    import sys

    import mysql.connector

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    for data in response:
        item = data.split(",")
        AcctNumber = item[0]
        FundName = item[2]
        Ticker = item[1]
        Shares = item[4].strip("$")
        Price = item[3].strip("$")
        datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','" + Ticker + "','" +  FundName + "','" + Shares + "','" + Price + "'")

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
    SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='CapitalOne' ORDER BY Account_Name, Account_Username"
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
