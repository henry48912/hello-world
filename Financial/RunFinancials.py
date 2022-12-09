import sys
from datetime import datetime
import mysql.connector
import os
import shutil

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

def GetLastDate(inst):

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "SELECT A.Date FROM Financial.Funds A "
        SQLStmt = SQLStmt + "INNER JOIN Financial.Accounts B ON A.Account_Number = B.Account_Number "
        SQLStmt = SQLStmt + "WHERE B.Account_Name='" + inst + "' "
        SQLStmt = SQLStmt + "ORDER BY A.Date DESC "
        SQLStmt = SQLStmt + "LIMIT 1"
        cursor.execute(SQLStmt)
        temp = list(cursor.fetchall())
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    LastDate = temp[0][0].strftime('%Y-%m-%d')
    
    return LastDate


def GetAccountList():

    conn1 = mysql.connector.connect(host="192.168.1.46", user="brent", password="hello", database="MWHData")

    try:
        cursor = conn1.cursor()
    except:
        print(sys.exc_info())

    try:
        SQLStmt = "SELECT Account_Name FROM Financial.Accounts"
        cursor.execute(SQLStmt)
        AccountList = list(sum(cursor.fetchall(), ()))
    except:
        if sys.exc_info()[1].msg[:13] == "Duplicate entry":
            print("Duplicate Entry")

    cursor.close()
    conn1.close()

    AccountList = sorted([*set(AccountList)])

    AccountList.remove('Fidelity')
    AccountList.remove('Chase')

    return AccountList


def prepareTextFile(DateToday):

    from datetime import timedelta

    StopWriting = False
    PastDate = datetime.now() - timedelta(5)
    PastDateStr = PastDate.strftime('%Y-%m-%d')
    source = '/home/brent/Documents/mysql_msgs/FinancialStatus.txt'
    destination = '/home/brent/Documents/mysql_msgs/oldStatus.txt'
    with open(source, 'r') as input:
        with open(destination, 'w') as output:
            for line in input:
                if line.startswith('Starting Financial Update Process for ' + PastDateStr):
                    StopWriting = True
                if StopWriting == False:
                    output.write(line)

    input.close()
    output.close()
    os.remove(source)



if __name__ == '__main__':

    AccountList = GetAccountList()
    DateToday = datetime.now().strftime('%Y-%m-%d')
    TimeNow = datetime.now().strftime('%H:%M')
    prepareTextFile(DateToday)
    msgfile = open('/home/brent/Documents/mysql_msgs/newStatus.txt', 'w+')
    msgfile.write("Starting Financial Update Process for " + DateToday + " @" + TimeNow + " from Ubuntu\n")

    for UpdateLoops in range(1, 5):

        msgfile.write("\nUpdate Loop " + str(UpdateLoops) + "\n")

        for Account in AccountList:

            if UpdateLoops == 1:
                msgfile.write("Reviewing " + Account + "\n")

            LastDate = GetLastDate(Account)

            if LastDate != DateToday:

                if UpdateLoops == 1:
                    msgfile.write("Attempting to update\n")

                os.system("/home/brent/Documents/Applications/Financial/.venv/bin/python /home/brent/Documents/Applications/Financial/Auto_"+Account+".py")

                LastDate = GetLastDate(Account)
                if LastDate != DateToday:
                    msgfile.write("Updating " + Account + ": Failed\n")
                else:
                    msgfile.write("Updating " + Account + ": Success\n")


    msgfile.write("\n\n\n")
    msgfile.close()

    with open('/home/brent/Documents/mysql_msgs/FinancialStatus.txt', 'w') as new:
        with open('/home/brent/Documents/mysql_msgs/newStatus.txt') as prefix:
            new.write(prefix.read())
        with open('/home/brent/Documents/mysql_msgs/oldStatus.txt') as old:
            new.write(old.read())

    os.remove('/home/brent/Documents/mysql_msgs/newStatus.txt')
    os.remove('/home/brent/Documents/mysql_msgs/oldStatus.txt')
