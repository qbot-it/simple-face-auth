from sqlalchemy import String, Column, Integer, JSON
from ...database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key=True)
    email = Column(String(), nullable=False, unique=True)
    descriptor = Column(JSON(), nullable=False, unique=False)
