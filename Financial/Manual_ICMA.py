import time
from datetime import datetime
import sys
import mysql.connector

def SendEmail(msgText):

    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import smtplib
    import ssl

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
    from pyppeteer import launch
    from bs4 import BeautifulSoup
    import time
    import sys

    async def ETrade():

        FundData = []

        browser = await launch(headless=False, executablePath='/usr/bin/google-chrome', userDataDir="/home/brent/Documents/")
        page = await browser.newPage()
        await page.setViewport({"width": 1920, "height": 1080})
        await page.goto("https://retirement.financialtrans.com/msq/")
        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                userid = await page.querySelector(["#input-userid"])
                await userid.type(Accounts[0][3])
                pword = await page.waitForXPath("//*[@id='input-password']")
                await pword.type(Accounts[0][4])
                button = await page.waitForXPath("//*[@id='login-button']")
                await button.click()
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("ICMA: Unable to sign in for 30 seconds")
                    sys.exit()


#******************************************************************************************
# 1st Account

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                await page.goto("https://retirement.financialtrans.com/msq/my-portfolio")
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("ICMA: Unable to access 1st account page for 30 seconds")
                    sys.exit()

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                AcctNumber = "303874"
                Symbol = ""
                for funds in range(1, 2):
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr[1]/td[1]/span[1]/span[2]/span")
                    Name = await page.evaluate('el => el.textContent', element)
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[4]")
                    Quantity = await page.evaluate('el => el.textContent', element)
                    Quantity = Quantity.replace('\n', '').replace(',','').replace(' ','')
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[5]/text()")
                    Price = await page.evaluate('el => el.textContent', element)
                    Price = Price.replace('\n', '').replace(',','').replace(' ','').replace('$','')
                    FundData.append(AcctNumber + ',' + Symbol + ',' + Name + ',' + Price + ',' + Quantity)
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("ICMA: Unable to access funds for 1st account for 30 seconds")
                    sys.exit()

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                await page.goto("https://retirement.financialtrans.com/msq/participant-account")
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("Chase: Unable to get back to home screen from 1st account for 30 seconds")
                    sys.exit()

#******************************************************************************************
# 2nd Account

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                element = await page.waitForSelector(["#dropdown-icon-myaccount-actions-dropdown-menu-4 > span"], visible=True)
                await element.click()
                element = await page.waitForXPath("//*[@id='my-accounts-my-portfoliomyaccount-actions-dropdown-menu-4']")
                await element.click()
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("Chase: Unable to access 2nd account for 30 seconds")
                    sys.exit()

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                AcctNumber = "301011"
                Symbol = ""
                for funds in range(1, 6, 2):
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[1]/span[1]/span[2]/span")
                    Name = await page.evaluate('el => el.textContent', element)
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[4]")
                    Quantity = await page.evaluate('el => el.textContent', element)
                    Quantity = Quantity.replace('\n', '').replace(',','').replace(' ','')
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[6]/text()")
                    Balance = await page.evaluate('el => el.textContent', element)
                    Balance = Balance.replace('\n', '').replace(',','').replace(' ','').replace('$','')
                    Price = str(int(float(Balance) / float(Quantity) * 1000000))
                    Price = Price[:len(Price)-6] + "." + Price[len(Price)-6:]
                    FundData.append(AcctNumber + ',' + Symbol + ',' + Name + ',' + Price + ',' + Quantity)
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("Chase: Unable to access funds for 2nd account for 30 seconds")
                    sys.exit()

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                await page.goto("https://retirement.financialtrans.com/msq/participant-account")
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("Chase: Unable to get back to home screen from 2nd account for 30 seconds")
                    sys.exit()



#******************************************************************************************
# 3rd Account

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                element = await page.waitForSelector(["#dropdown-icon-myaccount-actions-dropdown-menu-5 > span"], visible=True)
                await element.click()
                element = await page.waitForXPath("//*[@id='my-accounts-my-portfoliomyaccount-actions-dropdown-menu-5']")
                await element.click()
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("Chase: Unable to access 3rd account for 30 seconds")
                    sys.exit()

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                AcctNumber = "107602"
                Symbol = ""
                for funds in range(1, 23, 2):
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[1]/span[1]/span[2]/span")
                    Name = await page.evaluate('el => el.textContent', element)
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[4]")
                    Quantity = await page.evaluate('el => el.textContent', element)
                    Quantity = Quantity.replace('\n', '').replace(',','').replace(' ','')
                    element = await page.waitForXPath("//*[@id='printMe']/table/tbody/tr["+str(funds)+"]/td[6]/text()")
                    Balance = await page.evaluate('el => el.textContent', element)
                    Balance = Balance.replace('\n', '').replace(',','').replace(' ','').replace('$','')
                    Price = str(int(float(Balance) / float(Quantity) * 1000000))
                    Price = Price[:len(Price)-6] + "." + Price[len(Price)-6:]
                    FundData.append(AcctNumber + ',' + Symbol + ',' + Name + ',' + Price + ',' + Quantity)
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("Chase: Unable to access funds for 3rd account for 30 seconds")
                    sys.exit()

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                await page.goto("https://retirement.financialtrans.com/msq/participant-account")
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 30:
                    SendEmail("Chase: Unable to get back to home screen from 3rd account for 30 seconds")
                    sys.exit()

#******************************************************************************************

        WriteData(FundData, datetime.now())

        await browser.close()

    asyncio.get_event_loop().run_until_complete(ETrade())

def WriteData(response, dateStr):

    import mysql.connector
    import sys

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

    cursor.close()
    conn1.close()



conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

try:
    cursor = conn1.cursor()
except:
    print(sys.exc_info())

try:
    SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='ICMA' AND Account_Type='Investment' ORDER BY Account_Name, Account_Username"
    cursor.execute(SQLStmt)
    Accounts = list(cursor.fetchall())
except:
    if sys.exc_info()[1].msg[:13] == "Duplicate entry":
        print("Duplicate Entry")

cursor.close()
conn1.close()

ReadData(Accounts)