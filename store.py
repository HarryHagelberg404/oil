import csv
from scrape import scrape_oil_price
from datetime import datetime


def store_oil_price(price):
    with open("oil_prices.csv", "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), price])


# Example usage
price = scrape_oil_price()
store_oil_price(price)
