import os
import smtplib
import json

def send_email(subject, body):
    smtp_server = os.environ.get("SMTP_SERVER")
    port = os.environ.get("SMTP_PORT")
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")

    if not all([smtp_server, port, email, password]):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "email_config.json")
        with open(config_path, "r") as file:
            config = json.load(file)
        smtp_server = smtp_server or config["smtp_server"]
        port = port or config["port"]
        email = email or config["email"]
        password = password or config["password"]

    port = int(port)

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(email, password)
        message = f"Subject: {subject}\nFrom: {email}\n\n{body}"
        server.sendmail(email, email, message)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    subject = os.environ.get("EMAIL_SUBJECT", "New Vehicle Data")
    intro = os.environ.get("EMAIL_BODY_MESSAGE", "Here are the latest vehicle data!")

    from process_data import process_data
    here = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(here, "..", "data", "fetched_data.json")
    vehicle_data = process_data(json_path)

    body = f"{intro}\n\n{vehicle_data}".strip() if vehicle_data else intro
    send_email(subject, body)
