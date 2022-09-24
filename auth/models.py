from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, Numeric
from sqlalchemy_utils import ChoiceType, EmailType, URLType

from config.db import Base


class Token(BaseModel):
    access_token: str
    token_type: str


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    email = Column(EmailType, index=True, nullable=False, unique=True)
    name = Column(String(20), index=False, nullable=True)
    phone = Column(Numeric, nullable=False, default=-1)
    picture = Column(URLType, nullable=True)

    # Extra

    college = Column(String(30), nullable=True)
    course = Column(String(30), nullable=True)
    semester = Column(ChoiceType([(f"s{i}", f"S{i}") for i in range(1, 11)]), nullable=True)
    tshirt = Column(ChoiceType([(s, s.upper()) for s in ["s", "m", "l", "xl", "xxl"]]), nullable=True)
    linkedin = Column(URLType, nullable=True)
    github = Column(URLType, nullable=True)
    first_hackathon = Column(Boolean, nullable=True)
    experience = Column(String(120), nullable=True)
