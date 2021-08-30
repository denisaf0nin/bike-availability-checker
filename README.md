# Bike Stock Availability Checker

This is an example of an automated availability checker running on Heroku.

[The item in question](https://www.decathlon.lt/lt/unlinked/312397-66419-gravel-dviratis-120-su-diskiniai-stabdziais.html#/demodelsize-200m/demodelcolor-8575940?queryID=ecec0e2851f6f79ab57e376ac4c6c656&objectID=2962861) is out of stock and the retailer's website does not allow to subscribe to availablity updates.

What should the script do:
1. Go to website every 15 minutes and check if any frame size is available
2. If it is, send me an e-mail
3. If not, send emails at certain hours of the day (just so I know the script is still running)

It's also important to run it from the cloud, so I'll be using Heroku for that. 

The piece of HTML code that contains relevant information looks like this:

![Screenshot 2021-07-26 151313](https://user-images.githubusercontent.com/59995500/126987355-a27567bc-9de1-4c77-86ef-a31ba8a8f5cc.jpg)


    <select
          class="form-control form-control-select js-select-size js-select2"
          id="group_5"
          data-product-attribute="5"
          name="group[5]">
          
      <option value="" disabled>Pasirinkite dydį </option>
      <option value="5698" title="L" data-stock="disabled"> L </option>
      <option value="5697" title="M" data-stock="disabled"> M </option>
      <option value="5696" title="S" data-stock="disabled"> S </option>
      <option value="5699" title="XL" data-stock="disabled"> XL </option>
      <option value="5705" title="XS" data-stock="disabled"> XS </option>
    
    </select>

I am using requests to connect to the web page and BeautifulSoup to parse HTML code. I am looking for ```<select>``` tag with ```id="group_5"``` and get a list of ```option``` tags from it, extracting values of ```title``` and ```data-stock```. 

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

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
      
This function returns two objects - ```avail_dict``` - which is a dictionary with key-value pairs ```{Size: Availability}```, and a boolean ```is_avail```, indicating if any size is available. If an exception is raised, ```send_message()``` function is triggered. This function takes ```subject``` and ```text``` inputs and sends me an e-mail:
  
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
  
(Username, Password, and Recipient data is stored at Heroku's Config Vars)

Next I defined two functions - one for regular checks every 15 minutes, and another for sending an e-mail regardless of availability at set hours:

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

Both are using ```send_message()``` function, and there is another piece of the puzzle - ```create_message()``` function that takes ```avail_dict``` and ```is_avail``` variables (returned by ```availability_check()```) and generates ```subject``` and ```text``` inputs for ```send_message()```:

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
        
Finally, the two functions ```regular_check()``` and ```scheduled_report``` are added as jobs for ```APScheduler``` to run at defined intervals:

  
    from apscheduler.schedulers.blocking import BlockingScheduler
    from main import regular_check, scheduled_report

    scheduler = BlockingScheduler()

    regular_check = scheduler.add_job(regular_check, 'interval', minutes=15)
    scheduled_report = scheduler.add_job(scheduled_report, 'cron', hour="12,15,18,22", timezone='Europe/Vilnius')

    scheduler.start()
    
```Procfile``` instructs Heroku to run ```scheduler.py``` script, that in turn uses ```regular_check()``` and ```scheduled_report()``` functions from ```main.py```.

And here is an example of an e-mail being sent:

![Screenshot 2021-07-26 151335](https://user-images.githubusercontent.com/59995500/126987265-f5da96eb-64af-4b69-a8a2-3b4ebfb95364.jpg)






