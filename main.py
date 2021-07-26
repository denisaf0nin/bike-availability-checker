import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import smtplib
import os
import sys

tz = pytz.timezone('Europe/Vilnius')

link = "https://www.decathlon.lt/lt/unlinked/312397-66419-gravel-dviratis-120-su-diskiniai-stabdziais.html#/demodelsize-200m/demodelcolor-8575940?queryID=ecec0e2851f6f79ab57e376ac4c6c656&objectID=2962861"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}


def create_message(is_avail, avail_dict):
    subject = "Bike Check: "
    if is_avail:
        subject += 'AVAILABLE!!!'
    else:
        subject += 'Not in Stock.'
    now = datetime.now(tz)
    text = str(now.strftime("%d/%m/%Y %H:%M:%S<br>"))
    for k, v in avail_dict.items():
        line = str(k + ' - ' + v + '<br>')
        text += line
    return subject, text


def send_message(subject, text):
    USERNAME = os.environ['USERNAME']
    PASSWORD = os.environ['PASSWORD']
    RECIPIENT = os.environ['RECIPIENT']

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(USERNAME, PASSWORD)

    # message to be sent
    message_info = "\r\n".join(["from: " + USERNAME,
                                "subject: " + subject,
                                "to: " + RECIPIENT,
                                "mime-version: 1.0",
                                "content-type: text/html"])

    content = message_info + "\r\n\r\n" + text
    s.sendmail(USERNAME, RECIPIENT, content)
    s.quit()


def availability_check():
    page = requests.get(link, headers=headers)
    avail_dict = {}
    is_avail = False

    if page.status_code != 200:
        error_message = 'Something went wrong: page code ' + str(page.status_code)
        send_message('Bike Bot Error:', error_message)

    try:
        soup = BeautifulSoup(page.content, "html.parser")
        lst = list(soup.find("select", id="group_5").find_all('option'))

        for i in lst:
            if i.get('value') != "":
                size = i.get("title")
                avail = 'Not in stock' if i.get("data-stock") == 'disabled' else 'AVAILABLE!'
                avail_dict[size] = avail

        if "AVAILABLE!" in avail_dict.values():
            is_avail = True
    except:
        error_message = "Something went wrong at get_info stage"
        send_message('Bike Bot Error:', error_message)

    return is_avail, avail_dict


def regular_check():
    is_avail, avail_dict = availability_check()
    print('Regular check is running')
    sys.stdout.flush()
    if is_avail:
        s, t = create_message(is_avail, avail_dict)
        send_message(s, t)


def scheduled_report():
    is_avail, avail_dict = availability_check()
    s, t = create_message(is_avail, avail_dict)
    send_message(s, t)
