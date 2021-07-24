import requests
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
import smtplib
import keyring

#keyring.set_password("not.even.denis", "not.even.denis@gmail.com", "XXXXX")

link = "https://www.decathlon.lt/lt/unlinked/312397-66419-gravel-dviratis-120-su-diskiniai-stabdziais.html#/demodelsize-200m/demodelcolor-8575940?queryID=ecec0e2851f6f79ab57e376ac4c6c656&objectID=2962861"
# link = "https://www.decathlon.lt/lt/triatlonas-dviraciai/301919-33926-moteriskas-plento-dviratis-triban-easy.html#/demodelsize-200s/demodelcolor-8602202?queryID=497163abab43c35c3aea8f53c7cadd42&objectID=4118519"

html_class = "form-control form-control-select js-select-size js-select2"
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

page = requests.get(link, headers=headers)


def check():
    code = page.status_code
    if code != 200:
        error_message = 'Something went wrong: page code ' + str(code)
    else:
        error_message = ""

def regular_message():
    subject = "Bike Check: "
    if is_avail:
        subject += 'AVILABLE!!!'
    else:
        subject += 'Not in Stock.'
    now = datetime.now()
    text = str(now.strftime("%d/%m/%Y %H:%M:%S<br>"))
    for k, v in avail_dict.items():
        line = str(k + ' - ' + v + '<br>')
        text += line
    return subject, text

def send_message(subject, text):
    username = 'not.even.denis@gmail.com'
    #password = keyring.get_password('not.even.denis', username)
    password = 'mybot2021'

    recipient = 'denisafonin.spb@gmail.com'

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(username, password)

    # message to be sent
    headers = "\r\n".join(["from: " + username,
                           "subject: " + subject,
                           "to: " + recipient,
                           "mime-version: 1.0",
                           "content-type: text/html"])

    content = headers + "\r\n\r\n" + text
    s.sendmail(username, recipient, content)
    s.quit()

def get_info():
    global is_avail
    soup = BeautifulSoup(page.content, "html.parser")
    lst = list(soup.find("select", id="group_5").find_all('option'))

    for i in lst:
        if i.get('value') != "":
            size = i.get("title")
            avail = 'Not in stock' if i.get("data-stock") == 'disabled' else 'AVAILABLE!'
            avail_dict[size] = avail

    if "AVAILABLE!" in avail_dict.values():
        is_avail = True

    if is_avail:
        s, t = regular_message()
        send_message(s, t)





# Main logic

while True:
    page = requests.get(link, headers=headers)

    avail_dict = {}
    error_message = ""
    is_avail = False

    if page.status_code != 200:
        error_message = 'Something went wrong: page code ' + str(page.status_code)

    try:
        get_info()
    except:
        error_message = "Something went wrong at get_info stage"
        send_message('Bike Bot Error', error_message)
        break

    try:
        subject, text = regular_message()
        send_message(subject, text)
    except:
        error_message = "Something went wrong at get_info stage"
        send_message('Bike Bot Error', error_message)
        break

    sleep(360)


