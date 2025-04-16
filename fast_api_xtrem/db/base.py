from sqlalchemy.ext.declarative import declarative_base

# Créer la base une seule fois, ici
Base = declarative_base()


def get_base():
    return Base
