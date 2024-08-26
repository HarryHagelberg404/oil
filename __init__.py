import scrape
import send


def main():
    # Scrape the oil price
    scrape.main()

    # Send the report via email
    send.main()


if __name__ == "__main__":
    main()
