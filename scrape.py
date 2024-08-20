import requests
from bs4 import BeautifulSoup


# Step 1: Scrape Oil Price Data
def scrape_oil_price():
    url = "https://example.com/oil-prices"  # Replace with the actual URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Replace the following with the actual scraping logic
    price_tag = soup.find("span", {"id": "brent-price"})
    price = price_tag.text if price_tag else "N/A"

    print(f"Current Brent Crude Oil Price: {price}")
    return price


# Test the function
scrape_oil_price()
