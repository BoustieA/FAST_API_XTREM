from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

Base = declarative_base()

class Utilisateur(Base):
    __tablename__ = "Utilisateur"
    
    Id_Utilisateur = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    pswd = Column(String(50), nullable=False)