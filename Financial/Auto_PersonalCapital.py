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
    driver.maximize_window()
    time.sleep(5)

    try:
        pageText = driver.find_element(By.XPATH, "//*[@id='form-email']/fieldset/div[2]/label").text
        if pageText == "Email":
            button = driver.find_element(By.XPATH, "//*[@id='form-email']/fieldset/div[2]/div/input[5]")
            button.clear()
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//*[@id='form-email']/fieldset/div[3]/button")
            button.click()
            time.sleep(5)
        else:
            pageText = driver.find_element(By.XPATH, "//*[@id='form-password']/fieldset/div[6]/label").text
            if pageText == "Password":
                button = driver.find_element(By.XPATH, "//*[@id='form-password']/fieldset/div[6]/div/input[6]")
                button.clear()
                button.send_keys(account[0][4])
                button = driver.find_element(By.XPATH, "//*[@id='form-password']/fieldset/div[7]/button[1]")
                button.click()
                time.sleep(5)

    except:
        pageText = driver.find_element(By.XPATH, "//*[@id='form-password']/fieldset/div[6]/label").text
        if pageText == "Password":
            button = driver.find_element(By.XPATH, "//*[@id='form-password']/fieldset/div[6]/div/input[6]")
            button.clear()
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "//*[@id='form-password']/fieldset/div[7]/button[1]")
            button.click()
            time.sleep(5)
        else:
            print(sys.exc_info())
            print("Problem logging in")
            sys.exit()



    time.sleep(180)

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all("div", {"id":"js-sidebar-accounts"})
    datarow = []
    AcctNumber = account[0][1]
    dateStr = datetime.now()

    data = response[0].contents[0]
    for AcctSum in range(0,len(data)):
        try:
            subgroup = data.contents[AcctSum].text
            group = subgroup[subgroup.find(" "):subgroup.find("$")]
            group = group[group.find("\n")+1:]
            group = group[:group.find("\n")].strip()
        except:
            continue
        if group == "Cash" or group == "Investment" or group == "Credit" or group == "Loan" or group == "Other Asset":
            ReadBanks(data.contents[AcctSum])


    driver.close()


def WriteData(datarow):

    import mysql.connector
    import sys

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
        else:
            print(sys.exc_info())
            print(SQLStmt)

    cursor.close()
    conn1.close()


def CheckTotals(driver, TotalValue):

    driver.get('https://www.mybwlretirement.com/rsc-ang/accountOverview#!?myIrpPath=questionnaire')
    time.sleep(5)
    element = driver.find_element(By.XPATH, "//*[@id='accoverviewcontent']/div[1]/div[1]/app-balance-summary/app-skeleton/div[3]/div/div/div[1]/strong/div[1]")
    Total = int(element.text.replace(',','').strip('$'))
    if int(TotalValue) == Total:
        Okay = True
    else:
        Okay = False

def ReadBanks(dataStream):
    data = dataStream.contents[2].contents[1].contents
    for AcctSum in range(0,len(data)):
        try:
            subgroup = data[AcctSum].text.strip('\n')
            BankName = subgroup[:subgroup.find('\n')]
            BankName = BankName.replace("'", " ")
            if BankName == "":
                continue
            group = subgroup[subgroup.find("$")+1:]
            Balance = group[:group.find("\n")].replace(',','')
            if Balance == "":
                continue
            StartLoc = subgroup.find("Ending in ")
            if StartLoc == -1:
                AcctNum = subgroup[subgroup.find("$")+12:].strip().strip('\n')
            else:
                AcctNum = subgroup[subgroup.find("Ending in ")+10:]
            AcctNum = AcctNum[:AcctNum.find("\n")]
            datarow = ("'" + datetime.now().strftime('%Y-%m-%d') + "','PC-" + AcctNum + "','','" +  BankName + "','" + Balance + "','1'")
            WriteData(datarow)
        except:
            continue


if __name__ == '__main__':

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='PersonalCapital' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)