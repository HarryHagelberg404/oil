import scrape
import store
import report
import send


def main():
    # Scrape the oil price
    price = scrape.scrape_oil_price()

    # Store the oil price
    store.store_oil_price(price)

    # Generate the weekly report
    report_file = report.generate_report()

    # Send the report via email
    send.send_email(report_file)


if __name__ == "__main__":
    main()
