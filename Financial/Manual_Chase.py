from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime, timedelta
import mysql.connector
import sys

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

    import undetected_chromedriver

    driver = undetected_chromedriver.Chrome()
    driver.get(account[0][5])
    time.sleep(10)

    print(account[3][3])
    print(account[3][4])
    time.sleep(5)

    return driver
    
def ReadData(account):

    from bs4 import BeautifulSoup

    driver = login(account)

    LastDate = datetime.now() - timedelta(days=45)

    AcctBalance = driver.find_element(By.XPATH, "//*[@id='accountAvailableBalanceLinkPrimaryValue-773552328']").text
    line = ("'" + datetime.now().strftime('%Y-%m-%d') + "','" + account[3][1] + "','Cash','Cash','" + AcctBalance.replace(',','').replace('$','') + "','1'")
    WriteData(line)

    driver.get('https://secure08ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/accountSummaryDetail;accountDetailType=CHK;accountId=773552328;accountType=DDA')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"activityTableslideInActivity"})
            time.sleep(3)
            data = len(response[0].contents[3].contents)
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access transactions for Business Account for 30 seconds")
                sys.exit()

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            DateStr = response[0].contents[3].contents[0].contents[1].text.strip()
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access transactions for Business Account for 30 seconds")
                sys.exit()

    for item in range(0, data, 2):
        DateStr = response[0].contents[3].contents[item].contents[1].text.strip()
        if DateStr[:7] == "Pending":
            continue
        trans_date = datetime.strptime(DateStr, '%b %d, %Y')
        if trans_date < LastDate:
            break
        trans_desc = response[0].contents[3].contents[item].contents[2].text.strip()
        trans_desc = trans_desc[:119]
        trans_type = response[0].contents[3].contents[item].contents[3].text.strip()
        trans_amount = response[0].contents[3].contents[item].contents[4].text.strip()
        trans_amount = trans_amount.replace('$','').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        if trans_type == "ACH debit":
            trans_type = "Transfer"
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','593968305','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)

    driver.get('https://secure08ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/business')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            AcctBalance = driver.find_element(By.XPATH, "//*[@id='accountCurrentBalanceLinkWithReconFlyoutPrimaryValue-769570246']").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access Business Card for 30 seconds")
                sys.exit()
    line = ("'" + datetime.now().strftime('%Y-%m-%d') + "','" + account[2][1] + "','Credit','Card Balance','" + AcctBalance.replace(',','').replace('$','') + "','1'")
    WriteData(line)

    driver.get('https://secure08ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/accountSummaryDetail;accountDetailType=BCC;accountId=769570246;accountType=CARD')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"activityTableslideInActivity"})
            time.sleep(3)
            data = len(response[0].contents[3].contents)
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access transactions for Business Card for 30 seconds")
                sys.exit()
    for item in range(0, data, 2):
        DateStr = response[0].contents[3].contents[item].contents[1].text.strip()
        trans_date = datetime.strptime(DateStr, '%b %d, %Y')
        if trans_date < LastDate:
            break
        trans_desc = response[0].contents[3].contents[item].contents[2].text.strip()
        trans_desc = trans_desc[:119]
        trans_type = driver.find_element(By.XPATH, "//*[@id='categoryLink_202211301830224221111#20221111']").text
        trans_type = trans_type[:trans_type.find('\n')]
        trans_amount = response[0].contents[3].contents[item].contents[5].text.strip()
        trans_amount = trans_amount.replace('$','').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        if trans_type == "Bills & utilities":
            if trans_desc.startswith("AUTOMATIC PAYMENT"):
                trans_type = "Transfer"
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','4246315290282282','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)

    driver.get('https://secure08ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/business')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='convo-deck-sign-out']")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to return to home page for 30 seconds")
                sys.exit()
    button.click()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            button = driver.find_element(By.XPATH, "//*[@id='root']/header/div/div/div[2]/div[1]/div[3]/span/button")
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to logout for 30 seconds")
                sys.exit()
    button.click()
    print(account[0][3])
    print(account[0][4])

    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            AcctBalance = driver.find_element(By.XPATH, "//*[@id='accountCurrentBalanceLinkWithReconFlyoutPrimaryValue-878552482']").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access Amazon account for 30 seconds")
                sys.exit()
    line = ("'" + datetime.now().strftime('%Y-%m-%d') + "','" + account[1][1] + "','Credit','Card Balance','" + AcctBalance.replace(',','').replace('$','') + "','1'")
    WriteData(line)

    driver.get('https://secure07ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/multiProduct;flyout=accountSummary,878552482,CARD,BAC')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"activityTableslideInActivity"})
            time.sleep(3)
            data = len(response[0].contents[3].contents)
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access transactions for Amazon Card for 30 seconds")
                sys.exit()
    for item in range(0, data, 2):
        DateStr = response[0].contents[3].contents[item].contents[1].text.strip()
        trans_date = datetime.strptime(DateStr, '%b %d, %Y')
        if trans_date < LastDate:
            break
        trans_desc = response[0].contents[3].contents[item].contents[2].text.strip()
        trans_desc = trans_desc[:119].replace("'","")
        try:
            trans_type = response[0].contents[3].contents[item].contents[3].contents[1].contents[0].contents[0].attrs['text']
        except:
            trans_type = "Payment"
        trans_amount = response[0].contents[3].contents[item].contents[4].text.strip()
        trans_amount = trans_amount.replace('$','').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','4147400327473805','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)

    driver.get('https://secure08ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/multiProduct')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            AcctBalance = driver.find_element(By.XPATH, "//*[@id='principalBalanceLinkPrimaryValue-878552483']").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access Mortgage account for 30 seconds")
                sys.exit()
    line = ("'" + datetime.now().strftime('%Y-%m-%d') + "','" + account[0][1] + "','Loan','Loan Balance','" + AcctBalance.replace(',','').replace('$','') + "','1'")
    WriteData(line)

    driver.get('https://secure07ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/multiProduct;flyout=accountSummary,878552483,LOAN,HMG')
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            response = soup.find_all("table", {"id":"activityTableslideInActivity"})
            time.sleep(3)
            data = len(response[0].contents[3].contents)
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access transactions for Mortgage for 30 seconds")
                sys.exit()
    tryloop = True
    counter = 0
    while tryloop == True:
        try:
            DateStr = driver.find_element(By.XPATH, "//*[@id='transactionslideInActivity-0']/td[1]/span").text
            break
        except:
            time.sleep(1)
            counter = counter + 1
            if counter == 30:
                SendEmail("Chase: Unable to access transactions for Mortgage for 30 seconds")
                sys.exit()

    for item in range(0, 2, 1):
        DateStr = driver.find_element(By.XPATH, "//*[@id='transactionslideInActivity-"+str(item)+"']/td[1]/span").text
        trans_date = datetime.strptime(DateStr, '%b %d, %Y')
        if trans_date < LastDate:
            break
        trans_desc = driver.find_element(By.XPATH, "//*[@id='showDetails-slideInActivity"+str(item)+"']/span").text
        trans_desc = trans_desc[:119]
        trans_type = ""
        if trans_desc == "PAYMENT   PAYMENT":
            trans_type = "Contribution"
        if trans_desc == "PAYMENT":
            trans_type = "Contribution"
        trans_amount = driver.find_element(By.XPATH, "//*[@id='transactionslideInActivity-"+str(item)+"']/td[3]/span").text
        trans_amount = trans_amount.replace('$','').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','1014823874','" + trans_desc + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)

    driver.get('https://secure08ea.chase.com/web/auth/dashboard#/dashboard/overviewAccounts/overview/business')



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
        else:
            print(sys.exc_info())
            print(SQLStmt)

    cursor.close()
    conn1.close()



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


if __name__ == '__main__':

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='Chase' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    ReadData(Accounts)
