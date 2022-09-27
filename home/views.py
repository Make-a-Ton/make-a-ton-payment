from fastapi import APIRouter, Depends, Form
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.requests import Request

from auth.dependencies import get_current_user, login_redirect, create_user, get_user_by_email
from auth.models import User
from config.db import get_db
from config.variables import set_up
from home.models import Team
from home.utils import send_mails

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
async def create_profile(phone=Form(int), college=Form(str), course=Form(str), semester=Form(str),
                         tshirt=Form(str), linkedin=Form(str), github=Form(str), first_hackathon: bool = Form(False),
                         experience: str = Form(None), db: AsyncSession = Depends(get_db),
                         user=Depends(get_current_user)):
    if not user:
        return login_redirect("/profile")

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


@router.post("/team/create")
async def create_team(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
                      name=Form(str), member1: str = Form(None), member2: str = Form(None), member3: str = Form(None)):
    if not user:
        return login_redirect("/")

    members = set([str(m).lower().strip() for m in (member1, member2, member3) if m is not None and m != user.email])

    if len(members) > 3:
        return RedirectResponse("?error=Team can have only 4 members", status_code=307)

    if len(members) < 2:
        return RedirectResponse("?error=Team should have at least 3 members", status_code=307)

    members = {await get_user_by_email(u, db) or await create_user(u, "", -1, "", db) for u in members}

    for member in members:
        if member.team_id:
            return RedirectResponse(f"?error={member.email} already in a team", status_code=307)

    team = Team(name=name, lead=user.id, members=[m.id for m in members])
    db.add(team)

    await db.commit()
    await db.refresh(team)

    change = update(User).where(User.id == user.id).values(team_id=team.id)
    await db.execute(change)

    await db.commit()

    await send_mails(members, name, user.name, team.id)

    return RedirectResponse("/registered", status_code=303)


@router.get("/team/join")
async def create_team(request: Request, team_id: int, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    if not user:
        return login_redirect(f"/team/join?team_id={team_id}")

    context = {"request": request, "user": user}

    if user.team_id:
        context["error"] = "You are already in a team"
        return templates.TemplateResponse("join.html", status_code=400, context=context)

    team = await db.get(Team, team_id)

    if team is None:
        context["error"] = "Invalid team ID"
        return templates.TemplateResponse("join.html", status_code=400, context=context)

    if user.id not in team.members:
        context["error"] = "Sorry you are not invited"
        return templates.TemplateResponse("join.html", status_code=400, context=context)

    user.team_id = team.id

    change = update(User).where(User.id == user.id).values(team_id=team.id)
    await db.execute(change)

    await db.commit()

    return templates.TemplateResponse("join.html", status_code=200, context=context)


@router.get("/registered")
async def registered(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user:
        return login_redirect("/registered")

    if not user.team_id:
        RedirectResponse("/", status_code=307)

    team = await db.get(Team, user.team_id)

    lead = user if team.lead == user.id else await db.get(User, team.lead)
    members = [user if m == user.id else await db.get(User, m) for m in team.members if m != lead.id]

    context = {
        "app": config["name"],
        "request": request,
        "name": team.name,
        "team_id": team.id,
        "lead": lead,
        "members": members,
        "current_user": user
    }

    return templates.TemplateResponse("registered.html", context=context)


@router.get("/team/delete")
async def delete_team(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user:
        return login_redirect("/team/delete")

    context = {
        "request": request
    }

    if not user.team_id:
        context["error"] = "You don't have a team"
        return templates.TemplateResponse("delete.html", context=context)

    team = await db.get(Team, user.team_id)

    if team.lead != user.id:
        context["error"] = "You are not the team lead"
        return templates.TemplateResponse("delete.html", context=context)

    await db.delete(team)
    await db.commit()

    context["success"] = True
    return templates.TemplateResponse("delete.html", context=context)


@router.get("/")
def home(request: Request, user: User = Depends(get_current_user)):
    if not user:
        return login_redirect("/")

    if not (user.college and user.github and
            user.linkedin and user.course and
            user.tshirt and user.semester and user.phone != -1) or \
            (not user.first_hackathon and user.experience is None):
        return RedirectResponse("/profile", status_code=307)

    if user.team_id:
        return RedirectResponse("/registered", status_code=303)

    context = {
        "request": request
    }

    return templates.TemplateResponse("team.html", context=context)
