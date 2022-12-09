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
            button = driver.find_element(By.XPATH, "//*[@id='username']")
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//*[@id='password']")
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "//*[@id='signInBtn']")
            button.click()
            print(account[0][3])
            print(account[0][4])
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Citi: Unable to login for 30 seconds")
                sys.exit()

    return driver
    
def ReadData(account):

    driver = login(account)

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            tempStr = driver.find_element(By.XPATH, "//*[@id='cardAccountSelector0TileBody']").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Citi: Unable to access accounts for 30 seconds")
                sys.exit()
    temp = tempStr.split('\n')
    data = temp[2].replace(',','').strip('$')
    AcctNumber = account[0][1]

    WriteData(data, datetime.now(), AcctNumber)

    time.sleep(3)
    button = driver.find_element(By.XPATH, "//*[@id='center-view-area']/dashboard-recent-activity-tile/dashboard-recent-activity-tile-presentation/cds-tile/div/div[1]/div/div/div[2]/div/div[1]")
    button.click()
    GetTransactions(driver, AcctNumber)

    driver.close()


def GetTransactions(driver, AcctNumber):
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            data = driver.find_element(By.XPATH, "//*[@id='ums-transaction-tile']/table/ums-transaction-rows").text.strip()
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 60:
                SendEmail("Citi: Unable to access transactions for 60 seconds")
                sys.exit()
    for i in range(2, 100, 3):
        xpath = "//*[@id='ums-transaction-tile']/table/ums-transaction-rows/tr[" + str(i) + "]"
        try:
            data = driver.find_element(By.XPATH, xpath).text.strip()
        except:
            break
        tempStr = data.split('\n')
        if len(tempStr) < 3:
            break
        trans_dateStr = tempStr[0]
        trans_date = datetime.strptime(trans_dateStr, '%b %d, %Y')
        descStr = tempStr[1]
        amtStr = tempStr[len(tempStr)-3]
        trans_amount = amtStr.replace('$','').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        xpath = xpath + "/td[1]/span/ums-icon/div"
        button = driver.find_element(By.XPATH, xpath)
        button.click()
        time.sleep(3)
        DataRows = []
        for iRows in range(1,7):
            try:
                DataColumns = []
                xpath = "//*[@id='ums-transaction-tile']/table/ums-transaction-rows/tr[" + str(i+2) + "]/td[3]/div/div[2]/div[" + str(iRows) + "]/div[1]"
                DataColumns.append(driver.find_element(By.XPATH, xpath).text)
                xpath = "//*[@id='ums-transaction-tile']/table/ums-transaction-rows/tr[" + str(i+2) + "]/td[3]/div/div[2]/div[" + str(iRows) + "]/div[2]"
                DataColumns.append(driver.find_element(By.XPATH, xpath).text)
                DataRows.append(DataColumns)
            except:
                break
        for Row in DataRows:
            if Row[0] == "Spend Category":
                trans_type = Row[1]
            if Row[0] == "Type":
                trans_type = "Payment"
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + descStr + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            dropdown = driver.find_element(By.XPATH, "//*[@id='cds-dropdown-4-input']")
            dropdown.click()
            dropdown.send_keys(Keys.DOWN)
            dropdown.send_keys(Keys.RETURN)
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 60:
                SendEmail("Citi: Unable to access transactions for 60 seconds")
                sys.exit()

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            data = driver.find_element(By.XPATH, "//*[@id='ums-transaction-tile']/table/ums-transaction-rows/tr[3]").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 60:
                SendEmail("Citi: Unable to access transactions for 60 seconds")
                sys.exit()

    for i in range(2, 100, 3):
        xpath = "//*[@id='ums-transaction-tile']/table/ums-transaction-rows/tr[" + str(i) + "]"
        try:
            data = driver.find_element(By.XPATH, xpath).text
        except:
            break
        data = data.strip()
        tempStr = data.split('\n')
        trans_dateStr = tempStr[0]
        trans_date = datetime.strptime(trans_dateStr, '%b %d, %Y')
        descStr = tempStr[1]
        amtStr = tempStr[len(tempStr)-2]
        trans_amount = amtStr.replace('$','').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        xpath = xpath + "/td[1]/span/ums-icon/div"
        button = driver.find_element(By.XPATH, xpath)
        button.click()
        time.sleep(3)
        DataRows = []
        for iRows in range(1,7):
            try:
                DataColumns = []
                xpath = "//*[@id='ums-transaction-tile']/table/ums-transaction-rows/tr[" + str(i+2) + "]/td[3]/div/div[2]/div[" + str(iRows) + "]/div[1]"
                DataColumns.append(driver.find_element(By.XPATH, xpath).text)
                xpath = "//*[@id='ums-transaction-tile']/table/ums-transaction-rows/tr[" + str(i+2) + "]/td[3]/div/div[2]/div[" + str(iRows) + "]/div[2]"
                DataColumns.append(driver.find_element(By.XPATH, xpath).text)
                DataRows.append(DataColumns)
            except:
                break
        for Row in DataRows:
            if Row[0] == "Spend Category":
                trans_type = Row[1]
            if Row[0] == "Type":
                trans_type = "Payment"
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
            print(SQLStmt)

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
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='Citi' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)