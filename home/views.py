from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from auth.dependencies import get_current_user, login_redirect
from auth.models import User
from config.db import get_db
from config.variables import set_up

templates = Jinja2Templates(directory="home/templates")
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
def create_profile(phone=Form(int), college=Form(str), course=Form(str), semester=Form(str),
                   tshirt=Form(str), linkedin=Form(str), github=Form(str),first_hackathon=Form(bool),
                   experience=Form(str | None), db: AsyncSession=Depends(get_db)):

    pass


@router.get("/")
def home(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return login_redirect("/")

    if not (user.college and user.github and
            user.linkedin and user.course and
            user.tshirt and user.semester and user.phone == -1):
        return RedirectResponse("/profile", status_code=307)

    context = {
        "request": request
    }

    return templates.TemplateResponse("team.html", context=context)
