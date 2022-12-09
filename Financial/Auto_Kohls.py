import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import sys
import mysql.connector

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

    button = driver.find_element(By.XPATH, "//*[@id='username']")
    button.send_keys(account[0][3])
    button = driver.find_element(By.XPATH, "//*[@id='password']")
    button.send_keys(account[0][4])
    button = driver.find_element(By.XPATH, "//*[@id='login']")
    button.click()
    print(account[0][3])
    print(account[0][4])
    time.sleep(15)

    return driver
    
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



def ReadData(account):

    driver = login(account)

    tempStr1 = driver.find_element(By.XPATH, "//*[@id='full_body']/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/div/p/span[1]").text
    tempStr2 = driver.find_element(By.XPATH, "//*[@id='full_body']/section/div[3]/div[1]/div[2]/div[1]/div[1]/div/div/div/p/span[2]").text
    temp = tempStr1 + "." + tempStr2
    data = temp.replace(',','').replace('$','')
    AcctNumber = account[0][1]

    WriteData(data, datetime.now(), AcctNumber)

    button = driver.find_element(By.XPATH, "//*[@id='acc_table']/div[2]/div[3]/a")
    button.click()
    time.sleep(3)
    GetTransactions(driver, AcctNumber)

    driver.close()

def GetTransactions(driver, AcctNumber):
    for i in range(1, 100):
        xpath = "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]"
        try:
            data = driver.find_element(By.XPATH, xpath).text.strip()
        except:
            if i == 1:
                xpath = "//*[@id='acc_table']/div/div[2]/table/tbody/tr"
                try:
                    data = driver.find_element(By.XPATH, xpath).text.strip()
                except:
                    break
            else:
                break
        tempStr = data.split('\n')
        if tempStr[0] == "No data available":
            break
        trans_dateStr = tempStr[0]
        trans_date = datetime.strptime(trans_dateStr, '%m/%d/%Y')
        descStr = driver.find_element(By.XPATH, "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]/td[2]").text.strip()
        trans_type = driver.find_element(By.XPATH, "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]/td[3]").text.strip()
        amtStr = driver.find_element(By.XPATH, "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]/td[5]/span").text.strip()
        trans_amount = amtStr.replace('$','').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + descStr + "','" + trans_type + "','" + trans_amount + "'"
        WriteTrans(TransRecord)

    time.sleep(5)
    dropdown = driver.find_element(By.XPATH, "//*[@id='security_q']")
    dropdown.click()
    dropdown.send_keys(Keys.DOWN)
    dropdown.send_keys(Keys.RETURN)
    for i in range(1, 100):
        xpath = "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]"
        try:
            data = driver.find_element(By.XPATH, xpath).text.strip()
        except:
            if i == 1:
                xpath = "//*[@id='acc_table']/div/div[2]/table/tbody/tr"
                try:
                    data = driver.find_element(By.XPATH, xpath).text.strip()
                except:
                    break
            else:
                break
        tempStr = data.split('\n')
        trans_dateStr = tempStr[0]
        trans_date = datetime.strptime(trans_dateStr, '%m/%d/%Y')
        descStr = driver.find_element(By.XPATH, "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]/td[2]").text.strip()
        trans_type = driver.find_element(By.XPATH, "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]/td[3]").text.strip()
        amtStr = driver.find_element(By.XPATH, "//*[@id='acc_table']/div/div[2]/table/tbody/tr[" + str(i) + "]/td[5]/span").text.strip()
        trans_amount = amtStr.strip('$').replace(',','')
        if float(trans_amount) > 0:
            trans_amount = "-" + trans_amount
        else:
            trans_amount = trans_amount[1:]
        TransRecord = "'" + trans_date.strftime("%Y-%m-%d") + "','" + AcctNumber + "','" + descStr + "','" + trans_type + "','" + trans_amount + "'"
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



def WriteData(response, dateStr, AcctNumber):

    import mysql.connector
    import sys

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
            print(datarow)

    cursor.close()
    conn1.close()


if __name__ == '__main__':

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "SELECT * FROM Financial.Accounts WHERE Account_Name='Kohls' ORDER BY Account_Name, Account_Username"
        cursor.execute(SQLStmt)
        Accounts = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")
        else:
            print(sys.exc_info())
            print(SQLStmt)

    cursor.close()
    conn1.close()

    ReadData(Accounts)