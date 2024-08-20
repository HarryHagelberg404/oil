from jinja2 import Template
import csv


def generate_report():
    with open("oil_prices.csv", "r") as file:
        reader = csv.reader(file)
        data = list(reader)

    # Simple report template
    template = Template("""
    Weekly Oil Price Report
    =======================

    Date and Time          | Price
    -----------------------|-------
    {% for row in data %}
    {{ row[0] }}  | {{ row[1] }}
    {% endfor %}
    """)

    report = template.render(data=data)

    with open("weekly_report.txt", "w") as report_file:
        report_file.write(report)

    print("Weekly report generated!")


# Example usage
generate_report()
