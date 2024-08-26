import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import json
import re
from bs4 import BeautifulSoup


def download_html():
    url = "https://www.tradingview.com/symbols/NYMEX-UV1!/?contract=UVQ2024"
    file_name = os.path.join(os.getcwd(), "latest_oil_price.html")
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
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_content)
        print(f"Downloaded {file_name} successfully!")

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def extract_price_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the specific div with the price information
    details_div = soup.find('div', class_='details-i4FV5Ith')
    if not details_div:
        raise ValueError("Price information not found in the HTML content")

    # Extract the text content from the div
    text_content = details_div.get_text()

    # Use regex to extract the price
    match = re.search(r"current price of .*? is (\d+\.\d+)", text_content)
    if not match:
        raise ValueError("Price not found in the text content")

    price = float(match.group(1))
    return price


def is_swedish_bank_day():
    current_date = datetime.now().strftime("%Y-%m-%d")
    response = requests.get(f'https://api.riksbank.se/swea/v1/CalendarDays/{current_date}')
    response = json.loads(response.text)
    return response[0]["swedishBankday"]


def get_usd_to_sek_exchange_rate():
    response = requests.get("https://api.riksbank.se/swea/v1/Observations/Latest/sekusdpmi")

    if response.status_code == 200:
        data = response.json()
        return data["value"]
    else:
        raise Exception("Failed to retrieve exchange rate.")


def store_price_in_json(price, exchange_rate, json_file="daily_prices.json"):
    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "price": price,
        "exchange_rate": exchange_rate
    }

    try:
        with open(json_file, 'r') as file:
            prices = json.load(file)
    except FileNotFoundError:
        prices = []

    prices.append(data)

    with open(json_file, 'w') as file:
        json.dump(prices, file, indent=4)


def main():
    download_html()
    with open("latest_oil_price.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    price = ""
    exchange_rate = ""
    if is_swedish_bank_day():
        price = extract_price_from_html(html_content)
        exchange_rate = get_usd_to_sek_exchange_rate()

    store_price_in_json(price, exchange_rate)

    print(f"Price {price} USD stored successfully.")


main()
