from sqlalchemy import Column, String, Integer
from pydantic import BaseModel, constr, EmailStr
from fast_api_xtrem.db.db_manager import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    pswd = Column(String(50), nullable=False)


# Pydantic Models for request validation
class UserLogin(BaseModel):
    nom: constr(min_length=1, max_length=50)
    pswd: constr(min_length=8)  # Consider a minimum password length


class UserCreate(BaseModel):
    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)


class UserUpdate(BaseModel):
    nom: constr(min_length=1, max_length=50)
    email: EmailStr
    pswd: constr(min_length=8)  # added pswd
