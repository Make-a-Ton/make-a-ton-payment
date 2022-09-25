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

    members = set([str(m).lower().strip() for m in (member1, member2, member3) if m is not None])

    if len(members) > 3:
        return RedirectResponse("/?error='Team can have only 4 members'", status_code=307)

    team = Team(name=name, lead=user.id)

    db.add(team)
    await db.commit()

    await db.refresh(team)

    member_ids = []
    invalid = set()

    for member in members:
        user_m = await get_user_by_email(member, db) or await create_user(member, "", -1, "", db)

        if user_m.team_id and user_m.team_accepted:
            invalid.add(member)
            continue

        change = update(User).where(User.id == user_m.id).values(team_id=team.id, team_accepted=False)
        member_ids.append(user_m.id)

        await db.execute(change)

    change = update(Team).where(Team.id == team.id).values(members=member_ids)
    await db.execute(change)

    change = update(User).where(User.id == user.id).values(team_id=team.id, team_accepted=True)
    await db.execute(change)

    await db.commit()

    send_mails(members-invalid, name, user.name)

    return RedirectResponse("/registered", status_code=303)


@router.get("/registered")
async def registered(request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user:
        return login_redirect("/registered")

    if not user.team_id:
        RedirectResponse("/", status_code=307)

    user.team_accepted = True

    change = update(User).where(User.id == user.id).values(team_accepted=True)
    await db.execute(change)

    team = await db.get(Team, user.team_id)

    lead = await db.get(User, team.lead)
    members = [user if m == user.id else await db.get(User, m) for m in team.members if m != lead.id]

    context = {
        "app": config["name"],
        "request": request,
        "name": team.name,
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
            user.tshirt and user.semester and user.phone != -1 and
             user.experience != None):
        return RedirectResponse("/profile", status_code=307)

    if user.team_id:
        return RedirectResponse("/registered", status_code=303)

    context = {
        "request": request
    }

    return templates.TemplateResponse("team.html", context=context)
