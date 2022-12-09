from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import sys
import mysql.connector
import undetected_chromedriver.v2 as uc

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
    time.sleep(10)

    button = driver.find_element(By.XPATH, "//*[@id='username']")
    button.clear()
    button.send_keys(account[0][3])
    button = driver.find_element(By.XPATH, "//*[@id='password']")
    button.clear()
    button.send_keys(account[0][4])
    button = driver.find_element(By.XPATH, "//*[@id='formLogin']")
    button.click()
    time.sleep(15)

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)
    button = driver.find_element(By.XPATH, "//*[@id='dcSection']/div[2]/table/tbody/tr/td[4]/button")
    button.click()
    time.sleep(5)
    button = driver.find_element(By.XPATH, "//*[@id='balanceDetails']")
    button.click()
    time.sleep(5)
#    button = driver.find_element(By.XPATH, "//h1[@id='page-title']/span")
    dateStr = datetime.now()

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table", {"id":"accountBalanceByFund1"})
    datarow = []

    WriteData(response[0].contents[5], dateStr, account[0][1])
    GetTransactions(driver, account[0][1])


def GetTransactions(driver, AcctNumber):

    driver.get("https://secure.transamerica.com/ddol/authenticated/reports/transactionHistory.html")
    time.sleep(10)
    dropdown = driver.find_element(By.XPATH, "//*[@id='rangeSelect']")
    dropdown.click()
    dropdown.send_keys(Keys.UP)
    dropdown.send_keys(Keys.UP)
    dropdown.send_keys(Keys.RETURN)
    button = driver.find_element(By.XPATH, "//*[@id='main_layout']/form/div/div[2]/div[4]/div/button")
    button.click()
    time.sleep(10)
    ReadDividendFees(driver, AcctNumber)
    ReadAdminFees(driver, AcctNumber)
    ReadDividends(driver, AcctNumber)
    ReadFundFees(driver, AcctNumber)



def ReadDividendFees(driver, AcctNumber):

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table", {"id":"activity_details_bycontribution_Stock - Commission Fee"})
    datarow = response
    for item in range(1, len(response[0].contents)-6, 6):
        dateStr = response[0].contents[item].contents[1].contents[1].text[6:]
        trans_date = datetime.strptime(dateStr, '%m/%d/%Y')
        amtStr = response[0].contents[item+2].contents[3].contents[7].text
        trans_amount = amtStr.replace('$','')
        trans_desc = "Stock - Commission Fee"
        trans_type = "Dividend Fee"
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)



def ReadAdminFees(driver, AcctNumber):

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table", {"id":"activity_details_bycontribution_Administrative Fee - Per Account"})
    datarow = response
    for item in range(1, len(response[0].contents)-6, 6):
        dateStr = response[0].contents[item].contents[1].contents[1].text[6:]
        trans_date = datetime.strptime(dateStr, '%m/%d/%Y')
        amtStr = response[0].contents[item+2].contents[3].contents[7].text
        trans_amount = amtStr.replace('$','')
        trans_desc = "Administration Fee"
        trans_type = "Admin Fee"
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)



def ReadDividends(driver, AcctNumber):

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table", {"id":"activity_details_bycontribution_Periodic Dividends"})
    datarow = response
    for item in range(1, len(response[0].contents)-6, 6):
        dateStr = response[0].contents[item].contents[1].contents[1].text[6:]
        trans_date = datetime.strptime(dateStr, '%m/%d/%Y')
        amtStr = response[0].contents[item+2].contents[3].contents[7].text
        trans_amount = amtStr.replace('$','')
        trans_desc = "Stock - Commission Fee"
        trans_type = "Dividend Fee"
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)



def ReadFundFees(driver, AcctNumber):

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("table", {"id":"activity_details_bycontribution_Administrative Fee - Pro-Rata"})
    datarow = response
    for item in range(1, len(response[0].contents)-6, 6):
        dateStr = response[0].contents[item].contents[1].contents[1].text[6:]
        trans_date = datetime.strptime(dateStr, '%m/%d/%Y')
        amtStr = response[0].contents[item+4].contents[1].contents[3].contents[1].text
        trans_amount = amtStr.replace('$','').replace('\n', '').replace(' ', '').replace('\t', '')
        trans_desc = "Stock - Commission Fee"
        trans_type = "Dividend Fee"
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)



def WriteTrans(dataStr):

    import mysql.connector
    import sys

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



def WriteData(item, dateStr, AcctNumber):

    import mysql.connector
    import sys

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    NumberOfFunds = len(item.contents)
    for i in range(1,NumberOfFunds,2):
        if len(item.contents[i].contents) == 11:
            if float(item.contents[i].contents[7].text.replace(',','')) != 0:
                FundName = item.contents[i].contents[1].contents[2].text
                Ticker = ""
                Shares = item.contents[i].contents[7].text
                Shares = Shares.replace(',','').strip('$')
                Price = item.contents[i].contents[9].text
                Price = Price.replace(',','').strip('$')
                datarow = ("'" + dateStr.strftime('%Y-%m-%d') + "','" + AcctNumber + "','" + Ticker + "','" +  FundName + "','" + Shares.replace(',', '') + "','" + Price + "'")

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
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='Transamerica' AND Account_Type='Investment' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)