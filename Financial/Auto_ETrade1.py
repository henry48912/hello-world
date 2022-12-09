import sys
from datetime import datetime

import mysql.connector


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
    msg['Subject'] = "Financial Download Message"
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

    async def ETrade():

        FundData = []

        browser = await launch(headless=False, executablePath='/usr/bin/google-chrome', userDataDir="/home/brent/Documents/")
        page = await browser.newPage()
        await page.setViewport({"width": 1920, "height": 1080})
        await page.goto("https://us.etrade.com/e/t/user/login")
        time.sleep(5)
        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                userid = await page.querySelector(["#user_orig"])
                await userid.type(Accounts[0][3])
                pword = await page.waitForXPath("//*[@name='PASSWORD']")
                await pword.type(Accounts[0][4])
                button = await page.waitForXPath("//*[@id='logon_button']")
#                await button.click()
                await asyncio.wait([button.click(), page.waitForNavigation()])
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 60:
                    SendEmail("Etrade1: Unable to login for 30 seconds")
                    sys.exit()

#################################################################################################################################

        for NumberOfAccounts in range(1,4):
            tryloop = True
            counter = 0
            while tryloop == True:
                try:
                    element = await page.waitForXPath("//*[@id='application']/div/section[2]/div/div/div[1]/div[1]/div/div/div[" + str(NumberOfAccounts) + "]/div[1]/div[1]/div[1]/span[1]/span/a")
                    AcctName = await page.evaluate('el => el.textContent', element)
                    element = await page.waitForXPath("//*[@id='application']/div/section[2]/div/div/div[1]/div[1]/div/div/div[" + str(NumberOfAccounts) + "]/div[1]/div[1]/div[1]/span[2]/span[1]")
                    AcctShortNumber = await page.evaluate('el => el.textContent', element)
                    AcctName = AcctName[1:] + AcctShortNumber
                    element = await page.waitForXPath("//*[@id='application']/div/section[2]/div/div/div[1]/div[1]/div/div/div[" + str(NumberOfAccounts) + "]/div[1]/div[1]/div[1]/span[2]/span[2]/button")
                    await element.click()
#                    await asyncio.wait([element.click(), element.waitForNavigation()])
                    time.sleep(3)
                    element = await page.waitForXPath("//*[@id='application']/div/section[2]/div/div/div[1]/div[1]/div/div/div[" + str(NumberOfAccounts) + "]/div[1]/div[1]/div[1]/span[2]/span[1]")
                    AcctNumber = await page.evaluate('el => el.textContent', element)
                    break
                except:
                    time.sleep(1)
                    counter = counter + 1
                    if counter == 60:
                        SendEmail("Etrade1: Unable to get 1st account number for 30 seconds")
                        sys.exit()

            element = await page.waitForXPath("//*[@id='application']/div/section[2]/div/div/div[1]/div[1]/div/div/div[" + str(NumberOfAccounts) + "]/div[1]/div[1]/div[1]/span[1]/span/a")
#        await element.click()
            await asyncio.wait([element.click(), page.waitForNavigation()])
            time.sleep(2)
            await page.select('#accountDropdown', AcctName)
            time.sleep(5)
            tryloop = True
            counter = 0
            while tryloop == True:
                page_text = await page.content()#timePeriod > option:nth-child(4)
                soup = BeautifulSoup(page_text, 'html.parser')
                response = soup.find(id="application")
                dataread = response.contents[0].contents[4].contents[0].text
                loc = dataread.find("Viewing")
                if loc == -1 and dataread != "Legend":
                    Positions = 0
                else:
                    element = await page.waitForXPath("//*[@id='paginationViewingLabel']")
                    TextStr = await page.evaluate('el => el.textContent', element)
                    TextStr = TextStr[TextStr.find(" ")+1:]
                    TextStr = TextStr[TextStr.find(" ")+1:]
                    TextStr = TextStr[TextStr.find(" ")+1:]
                    TextStr = TextStr[:TextStr.find(" ")]
                    Positions = int(TextStr)
                testing = Positions
                for iRows in range(0,Positions):
                    try:
                        id1 = "symbolLink" + str(iRows)
                        id2 = "c" + str(iRows) + "_2"
                        id3 = "c" + str(iRows) + "_5"
                        element = await page.waitForXPath("//*[@id='" + id1 + "']")
                        Symbol = await page.evaluate('el => el.textContent', element)
                        Name = await page.evaluate('el => el.title', element)

                        element = await page.waitForXPath("//*[@id='" + id2 + "']/span")
                        Price = await page.evaluate('el => el.textContent', element)
                        element = await page.waitForXPath("//*[@id='" + id3 + "']/span")
                        Quantity = await page.evaluate('el => el.textContent', element)

                        FundData.append(AcctNumber + ',' + Symbol + ',' + Name + ',' + Price.strip("$") + ',' + Quantity.replace(',',''))

                    except:
                        break

                try:
                    id1 = "c" + str(iRows+1) + "_10"
                    element = await page.waitForXPath("//*[@id='" + id1 + "']/span")
                    Quantity = await page.evaluate('el => el.textContent', element)
                    FundData.append(AcctNumber + ',Cash,Cash,1,' + Quantity.replace(',','').replace("$", ""))
                    break
                except:
                    time.sleep(1)
                    counter = counter + 1
                    if counter == 60:
                        SendEmail("Etrade1: Unable to get 1st list of funds page for 30 seconds")
                        sys.exit()

            await page.goto("https://us.etrade.com/e/t/accounts/txnhistory")
            time.sleep(3)
            await page.select('#accountSelect', AcctName)
            time.sleep(2)
            for recordnumber in range(1,4):
                element = await page.waitForXPath("//*[@id='accountSelect']/optgroup/option[" + str(recordnumber) + "]")
                TestAcctName = await page.evaluate('el => el.textContent', element)
                if TestAcctName == AcctName:
                    Selected = await page.evaluate('el => el.selected', element)
                    if Selected == False:
                        await page.click('#accountSelect')
                        await page.keyboard.press('ArrowUp')
                        await page.keyboard.press('ArrowUp')
                        await page.keyboard.press('ArrowUp')
                        await page.keyboard.press('Enter')
                        element = await page.waitForXPath("//*[@id='accountSelect']/optgroup/option[" + str(recordnumber) + "]")
                        Selected = await page.evaluate('el => el.selected', element)
                        time.sleep(2)
                        while Selected != True:
                            await page.click('#accountSelect')
                            await page.keyboard.press('ArrowDown')
                            await page.keyboard.press('Enter')
                            element = await page.waitForXPath("//*[@id='accountSelect']/optgroup/option[" + str(recordnumber) + "]")
                            Selected = await page.evaluate('el => el.selected', element)
                            time.sleep(2)
            await page.select('#timePeriod', 'Last 90 days')
            selectElem = await page.querySelector('#timePeriod')
            await selectElem.type('Last 90 days')
            time.sleep(2)
            button = await page.waitForXPath("//*[@id='etContent']/form[2]/section[2]/div/div[4]/div/div/button")
            await asyncio.wait([button.click(), page.waitForNavigation()])

            tryloop = True
            counter = 0
            while tryloop == True:
                try:
                    page_text = await page.content()
                    soup = BeautifulSoup(page_text, 'html.parser')
                    response = soup.find(id="etContent").findAll("table")
                    datapoints = len(response[0].contents[3].contents)
                    break
                except:
                    time.sleep(1)
                    counter = counter + 1
                    if counter == 60:
                        SendEmail("Etrade1: Unable to read 1st set of transactions for 30 seconds")
                        sys.exit()

            for iTrans in range(1, datapoints, 2):
                TestStr = response[0].contents[3].contents[iTrans].contents[1].text
                if TestStr[:15] == "\nThere are no m":
                    break
                TransDateStr = response[0].contents[3].contents[iTrans].contents[1].text
                TransDate = datetime.strptime(TransDateStr, '%m/%d/%y')
                TransType = response[0].contents[3].contents[iTrans].contents[2].text
                TransDesc = " ".join(response[0].contents[3].contents[iTrans].contents[3].text.split())
                TransAmount = response[0].contents[3].contents[iTrans].contents[5].text
                TransRecord = "'" + TransDate.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + TransDesc + "','" + TransType + "','" + TransAmount + "'"
                WriteTrans(TransRecord)

            await page.goto("https://us.etrade.com/etx/hw/v2/accountshome?cnt=header_logon_startin_accounts")

#******************************************************************************************

        tryloop = True
        counter = 0
        while tryloop == True:
            try:
                page_text = await page.content()
                soup = BeautifulSoup(page_text, 'html.parser')
                response = soup.find(id="application").find("li")
                datedata = response.contents[2].text
                break
            except:
                time.sleep(1)
                counter = counter + 1
                if counter == 60:
                    SendEmail("Etrade1: Unable to read date information for 30 seconds")
                    sys.exit()

        WriteData(FundData, datetime.now())

        await browser.close()

    asyncio.get_event_loop().run_until_complete(ETrade())


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

    cursor.close()
    conn1.close()



conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

try:
    cursor = conn1.cursor()
except:
    print(sys.exc_info())

try:
    SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='ETrade1' AND Account_Type='Investment' ORDER BY Account_Name, Account_Username"
    cursor.execute(SQLStmt)
    Accounts = list(cursor.fetchall())
except:
    if sys.exc_info()[1].msg[:13] == "Duplicate entry":
        print("Duplicate Entry")

cursor.close()
conn1.close()

ReadData(Accounts)