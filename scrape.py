import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import os
import time


def download_html(url, file_name):
    try:
        chrome_options = Options()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(url)

        html_content = driver.page_source
        print(html_content)
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_content)
        print(f"Downloaded {file_name} successfully!")

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def scrape_oil_price():
    url = "https://www.barchart.com/futures/quotes/JUV*0/futures-prices"
    file_name = os.path.join(os.getcwd(), "oil_prices.html")

    now = datetime.now()
    formatted_date = now.strftime("%b %Y").upper()
    print(formatted_date)

    download_html(url, file_name)

    with open(file_name, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup)
    price_tag = soup.find("span", {"id": "brent-price"})
    price = price_tag.text if price_tag else "N/A"

    print(f"Current Brent Crude Oil Price: {price}")
    return price


scrape_oil_price()
