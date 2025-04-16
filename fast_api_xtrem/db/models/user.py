from sqlalchemy import Column, String, Integer
from fast_api_xtrem.db.db_manager import Base
from pydantic import BaseModel


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    pswd = Column(String(50), nullable=False)