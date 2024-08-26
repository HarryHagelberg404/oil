import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()


def load_last_30_prices(json_file="daily_prices.json"):
    # from 15 -14
    with open(json_file, 'r') as file:
        prices = json.load(file)

    # Sort the prices by date in ascending order
    prices.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))

    # Get the last 30 prices (or fewer if not available)
    return prices[-30:]


def create_html_report(prices):
    html = """
    <html>
    <body>
        <h2>Oil Price Report</h2>
        <table border="1" cellpadding="5" cellspacing="0">
            <tr>
                <th>Date</th>
                <th>Price (USD)</th>
                <th>Exchange rate</th>
            </tr>
    """

    for entry in prices:
        html += f"""
            <tr>
                <td>{entry['date']}</td>
                <td>{entry['price']} USD</td>
                <td>{entry['exchange_rate']} SEK/USD</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return html


def construct_email(subject, body, to_email, from_email):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_email)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))
    return msg


def main():
    last_30_prices = load_last_30_prices()
    report_html = create_html_report(last_30_prices)

    subject = "Daily Oil Price Report"
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    to_email = os.getenv("TO_EMAIL")
    from_email = os.getenv("FROM_EMAIL")

    try:
        msg = construct_email(subject, report_html, to_email, from_email)
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(username, password)
        to_email = to_email.split(",")
        for email in to_email:
            smtp_server.sendmail(from_email, email, msg.as_string())
        smtp_server.quit()
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email. Error: {e}")


if __name__ == "__main__":
    main()
