from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY
from sqlalchemy.orm import relationship

from config.db import Base


class Team(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    lead = Column(Integer, nullable=False)

    members = Column(ARRAY(Integer), default=dict)
