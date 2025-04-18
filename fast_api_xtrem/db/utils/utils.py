"""
Module de peuplement initial (seeding) pour la base de données.

Contient la fonction permettant d’insérer les rôles par défaut
dans la table `roles` si ceux-ci n’existent pas encore.
"""

from sqlalchemy.orm import sessionmaker

from fast_api_xtrem.db.models.role import Role


def seed_default_roles(engine, logger):
    """Alimente la table 'roles' si vide."""
    session_factory = sessionmaker(bind=engine)
    with session_factory() as session:
        existing_roles = {r.libelle for r in session.query(Role).all()}
        new_roles = []

        for role in ["admin", "membre"]:
            if role not in existing_roles:
                new_roles.append(Role(libelle=role))
                logger.info(f"Ajout du rôle : {role}")

        if new_roles:
            session.add_all(new_roles)
            session.commit()
            logger.success(
                f"🎉 Rôles insérés : {', '.join(r.libelle for r in new_roles)}"
            )
        else:
            logger.info("✅ Tous les rôles existent déjà")
