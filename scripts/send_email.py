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

smtp_server = config["smtp_server"]
    port = config["port"]
with open("../config/email_config.json", "r") as file:
        config = json.load(file)

port = int(port)

    try:
        server = smtplib.SMTP(smtp_server, port)
