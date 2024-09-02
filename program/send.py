import json
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import program.scrape as scrape
import os
from dotenv import load_dotenv
load_dotenv()


def update_last_30_prices(json_file="data/daily_prices.json"):
    update_json_with_accumulated_mean_price("data/daily_prices.json")


def load_last_30_prices(json_file="data/daily_prices.json"):
    with open(json_file, 'r') as file:
        prices = json.load(file)

    prices.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
    # from 15 -14
    # Make calculations and add to prices var
    today_date = datetime.now().strftime("%Y-%m-%d")
    filtered_entries = filter_entries_by_date(prices, today_date)
    return filtered_entries


def filter_entries_by_date(entries, day_to_calculate):
    current_date = datetime.strptime(day_to_calculate, "%Y-%m-%d")

    # Determine the start date based on the current date
    if current_date.day >= 15:
        start_date = current_date.replace(day=15)
    else:
        if current_date.month == 1:
            start_date = current_date.replace(year=current_date.year - 1, month=12, day=15)
        else:
            previous_month = current_date.month - 1
            start_date = current_date.replace(month=previous_month, day=15)

    # Filter entries that are within the start date and current date
    filtered_entries = [
        entry for entry in entries
        if start_date <= datetime.strptime(entry["date"], "%Y-%m-%d") <= current_date
    ]

    return filtered_entries


def calculate_accumulated_mean_price(entries):
    accumulated_sum = 0
    accumulated_count = 0

    for entry in entries:
        price = entry.get("price", None)

        if isinstance(price, (int, float)) and price != "":
            accumulated_sum += price
            accumulated_count += 1
            entry["accumulated_mean_price"] = accumulated_sum / accumulated_count
        else:
            entry["accumulated_mean_price"] = None

    return entries


def update_json_with_accumulated_mean_price(json_file_path):
    with open(json_file_path, 'r') as file:
        entries = json.load(file)

    # Calculate the accumulated mean price and update the entries
    updated_entries = calculate_accumulated_mean_price(entries)

    # Write the updated entries back to the JSON file
    with open(json_file_path, 'w') as file:
        json.dump(updated_entries, file, indent=4)

    logging.info(f"Updated JSON file at {json_file_path} with accumulated mean prices.")


def mean_currency(entries):
    exchange_rates = [
        entry["exchange_rate"] for entry in entries
        if isinstance(entry["exchange_rate"], (int, float)) and entry["exchange_rate"] != ""
    ]

    if not exchange_rates:
        return None  # Return None if there are no valid exchange rates

    mean_exchange_rate = sum(exchange_rates) / len(exchange_rates)
    return mean_exchange_rate


def mean_price(entries):
    prices = [
        entry["price"] for entry in entries
        if isinstance(entry["price"], (int, float)) and entry["price"] != ""
    ]

    if not prices:
        return None  # Return None if there are no valid prices

    mean_price = sum(prices) / len(prices)
    return mean_price


def latest_closing_price(entries):
    if not entries:
        return None  # Return None if the list is empty
    
    for entry in reversed(entries):
        price = entry.get("accumulated_mean_price", None)
        if isinstance(price, (int, float)) and price != "":
            return price
        

def create_html_report(prices):
    m_currency = mean_currency(prices)
    f_m_currency = f"{m_currency:.4f}"
    m_price = mean_price(prices)
    latest = f"{latest_closing_price(prices):.2f}"
    variable_price = int(m_price * m_currency)

    first_date_str = prices[0].get("date")
    last_date_str = prices[-1].get("date")
    first_date = datetime.strptime(first_date_str, "%Y-%m-%d")
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    first_date_formatted = first_date.strftime("%m-%d")
    last_date_formatted = last_date.strftime("%m-%d")
    year = last_date.year

    html = f"""
    <html>
    <body>
        <h2>Olje- och valutanoteringar {year}</h2>
        <h3>{first_date_formatted}- {last_date_formatted} {year}</h3>
        <br>
        <h3>Medelvärde USD                              {f_m_currency} SEK/USD</h3>
        <h3>Platts HSFO 3,5 % FOB Rotterdam Barges      {latest} USD/MT</h3>
        <h3>Prisvariabel                                {variable_price} SEK/MT</h3>
        <br>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Dag</th>
                <th>Ackumulerat medelvärde, USD/MT</th>
                <th>Platts HSFO 3,5 % FOB Rotterdam Barges USD/MT</th>
                <th>Sveriges Riksbanks valutakurs för USD/SEK</th>
            </tr>
    """

    for entry in prices:
        f_accumulated_price = entry['accumulated_mean_price']
        f_price = entry['price']
        f_exchange_rate = entry['exchange_rate']
        if entry['accumulated_mean_price'] is not None:
            f_accumulated_price = f"{entry['accumulated_mean_price']:.3f}"
        else:
            f_accumulated_price = "   "
            f_price = "   "
            f_exchange_rate = "   "

        html += f"""
            <tr>
                <td>{entry['date']}</td>
                <td>{f_accumulated_price}</td>
                <td>{f_price}</td>
                <td>{f_exchange_rate}</td>
            </tr>
        """

    html += """
        </table>
        <p>Data över bankdagar är hämtad från riksbanken, vilket betyder att det speglar den svenska marknaden.</p>
        <p>Efter flertalet stickprov anses Riksbankens API vara pålitlig källa. Vänligen dubbelkolla på Europeeiska centralbanken</p>
        <p>Datan för Platts HSFO 3,5 % FOB Rotterdam Barges är hämtad från <a href="https://www.barchart.com/futures/quotes/JUV*0">Barchart</a> samt <a href="https://www.tradingview.com/symbols/NYMEX-UV1!/?contract=UVQ2024">Tradingview</a></p>
    </body>
    </html>
    """

    return html


def construct_email(subject, body, to_email, from_email):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))
    return msg


def main():
    update_last_30_prices()
    if scrape.is_swedish_bank_day():

        last_30_prices = load_last_30_prices()
        report_html = create_html_report(last_30_prices)

        subject = "Daglig olje-rapport"
        username = os.getenv("USERNAME")
        password = os.getenv("PASSWORD")
        to_email = os.getenv("TO_EMAIL")
        from_email = os.getenv("FROM_EMAIL")

        try:
            msg = construct_email(subject, report_html, to_email, from_email)
            smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            smtp_server.login(username, password)
            to_email = to_email.split(",")
            smtp_server.sendmail(from_email, to_email, msg.as_string())
            smtp_server.quit()
            logging.info(f"Email successfully sent to {to_email}")
            logging.info(f"Email sent at time: {datetime.now()}")
        except Exception as e:
            logging.warning(f"Failed to send email. Error: {e}")
