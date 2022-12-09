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

    time.sleep(1)
    driver = undetected_chromedriver.Chrome()
    driver.get(account[0][5])
    time.sleep(1)
    driver.maximize_window()

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)

#*****************************************************************************************
#   Account 1
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            FundName = driver.find_element(By.XPATH, "//*[@id='home-details-content']/div/div/div[1]/div[2]/div[2]/div[2]/div/div[1]/div[2]/h1").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Zillow: Unable to access fund page for 30 seconds")
                sys.exit()

    Ticker = ""
    Shares = driver.find_element(By.XPATH, "//*[@id='home-details-content']/div/div/div[1]/div[2]/div[2]/div[2]/div/div[1]/span/span[2]/span/span").text
    Price = "1"
    Shares = Shares.replace(',','').strip('$')
    datarow = ("'" + datetime.now().strftime('%Y-%m-%d') + "','" + account[0][1] + "','" + Ticker + "','" +  FundName + "','" + Shares.replace(',', '') + "','" + Price + "'")

    WriteData(datarow)
#*****************************************************************************************


def WriteData(datarow):

    import math
    import sys

    import mysql.connector

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
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='Zillow' AND Account_Type='Other' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)
