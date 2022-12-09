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
            button = driver.find_element(By.XPATH, "//input[@id='ember388']")
            button.clear()
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//input[@id='ember391']")
            button.clear()
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "//button[@id='ember394']")
            button.click()
            time.sleep(25)
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("TastyWorks: Unable to login for 30 seconds")
                sys.exit()

    return driver
    
def ReadData(account):


    driver = login(account)

    driver.get('https://trade.tastyworks.com/index.html#/portfolioPage')
    dateStr = datetime.now()

    WriteData(driver, dateStr, account[0][1])


def WriteData(driver, dateStr, AcctNumber):

    import sys

    import mysql.connector
    from bs4 import BeautifulSoup

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            Ticker = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[2]/div[1]/div/div").text
            FundName = "Etherium"
            Shares = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[5]/span").text
            Shares = Shares[:len(Shares)-2]
            Price = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[1]/div/div[11]/div").text
            datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','" + Ticker + "','" +  FundName + "','" + Shares.replace(',', '') + "','" + Price + "'")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("TastyWorks: Unable to get account info for 30 seconds")
                sys.exit()

    try:
        SQLStmt = "INSERT INTO Financial.Funds VALUES (" + datarow + ")"
        cursor.execute(SQLStmt)
        conn1.commit()
    except:
        if sys.exc_info()[1].msg[:15] == "Duplicate entry":
            print("Duplicate Entry")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    Cash = soup.text[soup.text.find("Buy Pwr - Opt$")+14:]
    Cash = Cash[:Cash.find("\n")-1]
    datarow = []
    Shares = driver.find_element(By.XPATH, "/html/body/div/div[1]/div[1]/header/dl[3]/dd").text
    datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','Cash','Cash','" + Cash.replace(',', '') + "','1'")

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
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='TastyWorks' AND Account_Type='Investment' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)