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

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='app']/div[3]/main/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/input")
            button.clear()
            button.send_keys(account[0][3])
            button = driver.find_element(By.XPATH, "//*[@id='app']/div[3]/main/div/div[2]/div/div/div/div/div/div/div[2]/div[2]/input")
            button.clear()
            button.send_keys(account[0][4])
            button = driver.find_element(By.XPATH, "//*[@id='app']/div[3]/main/div/div[2]/div/div/div/div/div/div/div[3]/span[1]/button/div")
            button.click()
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                pageText = driver.find_element(By.XPATH, "//*[@id='app']/div[3]/main/div/div[2]/div/div/div/div/div/div/div[2]/div[1]/input").text
                if pageText == "ACCOUNTS":
                    continue
                else:
                    SendEmail("MERS: Unable to login for 30 seconds")
                    sys.exit()
    time.sleep(15)

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)

    button = driver.find_element(By.XPATH, "//*[@id='jfy-view-all-b1b1b9c1-c881-4065-text-43697b0255698']")
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='text-workoutLoading-label_0']")
#            button = driver.find_element(By.XPATH, "//*[@id='jfy-c2395ecf-a1cc-409f-a82d-c21d94b2cc4']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access home page for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='mode2']/ul/li[2]/a")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access home page for 30 seconds")
                sys.exit()
    button.click()

#*****************************************************************************************
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div[2]/ul/li/a[1]")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 1st account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='_plan6263341']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 1st account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='btn_change_plan_Go']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 1st account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("input", {"id":"_todate"})
            dateStr = datetime.now()
            response = soup.find_all("tbody", {"id":"acct_inv_bal_tbl_body"})
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 1st account for 30 seconds")
                sys.exit()

    WriteData(response, dateStr, account[1][1])
#*****************************************************************************************
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div[2]/ul/li/a[1]")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 2nd account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='_plan6583002']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 2nd account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='btn_change_plan_Go']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 2nd account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("input", {"id":"_todate"})
            dateStr = datetime.now()
            response = soup.find_all("tbody", {"id":"acct_inv_bal_tbl_body"})
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 2nd account for 30 seconds")
                sys.exit()

    WriteData(response, dateStr, account[0][1])
#*****************************************************************************************
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div[2]/ul/li/a[1]")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 3rd account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='_plan6578003']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 3rd account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='btn_change_plan_Go']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 3rd account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("input", {"id":"_todate"})
            dateStr = datetime.now()
            response = soup.find_all("tbody", {"id":"acct_inv_bal_tbl_body"})
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 3rd account for 30 seconds")
                sys.exit()

    WriteData(response, dateStr, account[2][1])
#*****************************************************************************************
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div[2]/ul/li/a[1]")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 4th account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='_plan6585204']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 4th account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='btn_change_plan_Go']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 4th account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("input", {"id":"_todate"})
            dateStr = datetime.now()
            response = soup.find_all("tbody", {"id":"acct_inv_bal_tbl_body"})
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 4th account for 30 seconds")
                sys.exit()

    WriteData(response, dateStr, account[3][1])
#*****************************************************************************************
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='main']/div[1]/div[2]/ul/li/a[1]")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 5th account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='_plan2222225']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 5th account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='btn_change_plan_Go']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 5th account for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("input", {"id":"_todate"})
            dateStr = datetime.now()
            response = soup.find_all("tbody", {"id":"acct_inv_bal_tbl_body"})
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("MERS: Unable to access 5th account for 30 seconds")
                sys.exit()

    WriteData(response, dateStr, account[3][1])


def WriteData(response, dateStr, AcctNumber):

    import mysql.connector
    import sys

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="Financial")
    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    for item in response:
        NumberOfFunds = len(item.contents)
        for i in range(1,NumberOfFunds, 2):
            TextStr = item.contents[i].text
            TextStr = TextStr[TextStr.find("\n")+1:]
            TextStr = TextStr[TextStr.find("\n")+1:]
            TextStr = TextStr[TextStr.find("\n")+1:]
            Balance = TextStr[:TextStr.find("\n")]
            Balance = Balance.strip()
            Balance = Balance.replace(',','').strip('$')
            Balance = int(float(Balance))
            if Balance > 0:
                FundName = item.contents[i].contents[1].text
                Ticker = ""
                Shares = item.contents[i].contents[5].text
                Shares = Shares.replace(',','').strip('$')
                Price = item.contents[i].contents[7].text
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
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='MERS' AND Account_Type='Investment' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)