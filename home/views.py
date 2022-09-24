import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import APIRouter, Depends, Form
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from auth.dependencies import get_current_user, login_redirect
from auth.models import User
from config.db import get_db
from config.variables import set_up

templates = Jinja2Templates(directory="home/templates")
ssl_context = ssl.create_default_context()
router = APIRouter()
config = set_up()


@router.get("/profile")
def profile(request: Request, user=Depends(get_current_user)):
    if not user:
        return login_redirect("/profile")

    context = {
        "user": user,
        "app": config["name"],
        "request": request
    }

    return templates.TemplateResponse("profile.html", context=context)


@router.post("/profile")
async def create_profile(phone=Form(int), college=Form(str), course=Form(str), semester=Form(str),
                         tshirt=Form(str), linkedin=Form(str), github=Form(str), first_hackathon: bool = Form(False),
                         experience=Form(str | None), db: AsyncSession = Depends(get_db),
                         user=Depends(get_current_user)):
    if not user:
        return login_redirect("/profile")

    if first_hackathon:
        experience = None

    if not first_hackathon and experience is None:
        return RedirectResponse("/profile?error='First Hackathon'", status_code=307)

    change = update(User).where(User.id == user.id).values(
        phone=phone,
        college=college,
        course=course,
        semester=semester,
        tshirt=tshirt,
        linkedin=linkedin,
        github=github,
        first_hackathon=first_hackathon,
        experience=experience
    )

    await db.execute(change)
    await db.commit()

    return RedirectResponse("/", status_code=303)


@router.get("/")
def home(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return login_redirect("/")

    if not (user.college and user.github and
            user.linkedin and user.course and
            user.tshirt and user.semester and user.phone != -1 and
            (user.first_hackathon and user.experience is None)):
        return RedirectResponse("/profile", status_code=307)

    context = {
        "request": request
    }

    return templates.TemplateResponse("team.html", context=context)


def create_team(user: User = Depends(get_current_user),
                name=Form(str), member1=Form(str | None), member2=Form(str | None), member3=Form(str | None)):
    if not user:
        return login_redirect("/")

    members = [m for m in (member1, member2, member3) if m is not None]

    with smtplib.SMTP_SSL(config["email"]["host"], config["email"]["port"], context=ssl_context) as server:
        server.login(config["email"]["user"], config["email"]["password"])

        for member in members:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Invite To Make A Ton"
            message["From"] = config["email"]["user"]
            message["To"] = member

            context = {
                "app": config["name"],
                "team": name
            }

            html = MIMEText(templates.get_template("email.html").render(context=context), "html")
            message.attach(html)

            server.sendmail(config["email"]["user"], member, message.as_string())

    return RedirectResponse("/registered", status_code=303)
