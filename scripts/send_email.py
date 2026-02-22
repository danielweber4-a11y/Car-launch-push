import smtplib
import json

def send_email(subject, body):
    with open("../config/email_config.json", "r") as file:
        config = json.load(file)

    smtp_server = config["smtp_server"]
    port = config["port"]
    email = config["email"]
    password = config["password"]

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(email, password)
        message = f"Subject: {subject}\n\n{body}"

        server.sendmail(email, email, message)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)

if __name__ == "__main__":
    send_email("Daily Car Launches", "Here are the latest car launches today!")