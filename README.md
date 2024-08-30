# Oil index

This program is to scrape a specific oil index price daily and then, store relevant data, create a report, and send to specified stakeholders.
Follow the following guide to get started.

## .env file:

```
USERNAME="your google mail without the @...."
PASSWORD="google app password"
TO_EMAIL="the emails you want to send to"
FROM_EMAIL="the email you are sending from"

```


## Install and run locally:

To be able to run the program you need chromedriver (for testing), please see the orchestration/ and setup.yml for how and where you should configure it


```pip install -r requirements.txt```

```python3 __init_scrape__.py```
```python3 __init_send__.py```


## Automation

If you wish to run the program daily on a physical/hosted resource, please take use of the /orchestration folder which takes use of ansible to configure the host to be able to run the scripts via cron.
