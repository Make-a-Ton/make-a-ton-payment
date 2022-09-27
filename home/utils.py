import asyncio
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Set

from starlette.templating import Jinja2Templates

from auth.models import User
from config.variables import set_up

ssl_context = ssl.create_default_context()
templates = Jinja2Templates(directory="home/templates")

config = set_up()


async def send_to_user(member: User, name: str, inviter: str, team_id: int, server):
    member = member.email
    message = MIMEMultipart("alternative")
    message["Subject"] = "Invite To Make A Ton"
    message["From"] = config["email"]["user"]
    message["To"] = member

    join_url = f"{config['protocol']}{config['domain']}:{config['port']}/team/join?team_id={team_id}"

    context = {
        "app": config["name"],
        "team": name,
        "join_url": join_url,
        "to": member.split("@")[0],
        "inviter": inviter
    }

    html = MIMEText(templates.get_template("email.html").render(**context), "html")
    text = MIMEText(join_url, "text")

    message.attach(text)
    message.attach(html)

    server.sendmail(config["email"]["user"], member, message.as_string())


async def send_mails(members: Set[User], name: str, inviter: str, team_id: int):
    with smtplib.SMTP_SSL(config["email"]["host"], config["email"]["port"], context=ssl_context) as server:
        server.login(config["email"]["user"], config["email"]["password"])

        await asyncio.gather(*[send_to_user(member, name, inviter, team_id, server) for member in members])
