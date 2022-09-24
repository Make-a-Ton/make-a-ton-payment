from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

import home.views
from auth import auth
from config.variables import set_up

app = FastAPI()
config = set_up()

origins = [
    f"{config['protocol']}{config['domain']}",
    f"{config['protocol']}{config['domain']}:{config['port']}"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if config['debug']:
    app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(home.views.router)
