import smtplib
from email.mime.text import MIMEText


def send_email(report_file):
    sender = "your_email@example.com"
    receiver = "receiver_email@example.com"
    subject = "Weekly Oil Price Report"

    with open(report_file, "r") as file:
        report_content = file.read()

    msg = MIMEText(report_content)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("your_email@example.com", "your_password")
        server.sendmail(sender, receiver, msg.as_string())

    print("Email sent!")


# Example usage
send_email("weekly_report.txt")
