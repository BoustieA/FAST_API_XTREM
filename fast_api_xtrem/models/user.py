from sqlalchemy import Column, String, Integer
from fast_api_xtrem.db.db_manager import Base
from pydantic import BaseModel


class Utilisateur(Base):
    __tablename__ = "Utilisateur"

    Id_Utilisateur = Column(Integer,
                            primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    pswd = Column(String(50), nullable=False)


class UtilisateurBase(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None
    pswd: Optional[str] = None

class UtilisateurLogin(BaseModel):
    nom: str
    pswd: str
