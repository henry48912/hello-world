import undetected_chromedriver.v2 as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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



def login(account):

    chrome_options = uc.ChromeOptions()
    userdatadir='/home/brent/Documents/Applications/Financial/~/Documents/Brent/Profile 1'
    userprofiledir='/home/brent/.config/google-chrome/Brent'
    chrome_options.add_argument("--user-data-directory={userdatadir}")
    chrome_options.add_argument("--profile-directory={userprofiledir}")
    chrome_options.add_argument("--start-maximized")

    driver = uc.Chrome(options=chrome_options)
    driver.get(account[0][5])
    time.sleep(5)
    button = driver.find_element(By.XPATH, "//*[@id='login']/div[1]/div[1]/button")
    button.click()
    time.sleep(5)
    driver.maximize_window()

    button = driver.find_element(By.XPATH, "//*[@id='username0']")
    button.clear()
    button.send_keys(account[0][3])
    button = driver.find_element(By.XPATH, "//*[@id='password1']")
    button.clear()
    button.send_keys(account[0][4])
    button = driver.find_element(By.XPATH, "//*[@id='accept']")
    button.click()
    time.sleep(5)

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)
    driver.get('https://invest.ameritrade.com/grid/p/site#r=positions')
    time.sleep(5)
    dateStr = datetime.now()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find(id="uniqName_45_0")
    for lineitem in range(1,len(response.contents[2].contents[3].contents), 2):
        datarow = []
        FundName = response.contents[2].contents[3].contents[lineitem].contents[1].text
        FundName = FundName.replace('\n','')
        Ticker = ""
        Shares = response.contents[2].contents[3].contents[lineitem].contents[3].contents[1].text
        Shares = Shares.replace('\n','').replace(',','').replace('$','')
        Price = "1"
        datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + account[0][1] + "','" + Ticker + "','" +  FundName + "','" + Shares.replace(',', '') + "','" + Price + "'")
        WriteData(datarow)

    response = soup.find(id='uniqName_45_1')
    for lineitem in range(1, len(response.contents[2].contents[3].contents), 2):
        datarow = []
        FundName = response.contents[2].contents[3].contents[1].contents[1].text
        FundName = FundName.replace('\n', '')
        Ticker = FundName
        Shares = response.contents[2].contents[3].contents[1].contents[5].contents[0].text
        Shares = Shares.replace(',','').strip('$')
        Price = response.contents[2].contents[3].contents[1].contents[9].text
        Price = Price.replace(',','').strip('$')
        datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + account[0][1] + "','" + Ticker + "','" +  FundName + "','" + Shares.replace(',', '') + "','" + Price + "'")
        WriteData(datarow)

    driver.get('https://invest.ameritrade.com/grid/p/site#r=home')
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 900)")
    button = driver.find_element(By.XPATH, "//*[@id='dijit_TitlePane_1_titleBarNode']/div/span[3]")
    button.click()
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table")
    for iTrans in range(3,len(response[6].contents[1].contents),2):
        transData = response[6].contents[1].contents[iTrans].text
        colData = transData.split("\n")
        TransDate = datetime.strptime(colData[1], '%m/%d/%y')
        AcctNumber = account[0][1]
        Description = colData[3]
        Amount = colData[2].replace(",","").replace("$","")
        TransType = "Trade"
        transStr = "'" + TransDate.strftime('%Y-%m-%d') + "','" + AcctNumber + "','" + Description + "','" + TransType + "','" + Amount + "'"

        WriteTransData(transStr)



def WriteTransData(transdata):

    import mysql.connector
    import sys

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



def WriteData(datarow):

    import mysql.connector
    import sys
    import math

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "INSERT INTO Financial.Funds VALUES (" + datarow + ")"
        cursor.execute(SQLStmt)
        conn1.commit()
    except:
        if sys.exc_info()[1].msg[:15] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()


if __name__ == '__main__':

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='TDAmeritrade' AND Account_Type='Investment' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)