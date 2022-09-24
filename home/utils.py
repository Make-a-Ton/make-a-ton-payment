import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Set

from starlette.templating import Jinja2Templates

from config.variables import set_up

ssl_context = ssl.create_default_context()
templates = Jinja2Templates(directory="home/templates")

config = set_up()


def send_mails(members: Set[str], name):
    with smtplib.SMTP_SSL(config["email"]["host"], config["email"]["port"], context=ssl_context) as server:
        server.login(config["email"]["user"], config["email"]["password"])

        for member in members:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Invite To Make A Ton"
            message["From"] = config["email"]["user"]
            message["To"] = member

            context = {
                "app": config["name"],
                "team": name,
                "join_url": f"{config['protocol']}{config['domain']}:{config['port']}"
            }

            html = MIMEText(templates.get_template("email.html").render(**context), "html")
            message.attach(html)

            server.sendmail(config["email"]["user"], member, message.as_string())
