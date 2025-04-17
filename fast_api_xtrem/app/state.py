"""
Module de gestion de l'état partagé de l'application FastAPI XTREM.

Ce module fournit la classe `AppState` qui permet de stocker,
récupérer et vérifier des objets dans un dictionnaire interne
utilisé comme conteneur d'état global. Cela permet de partager
des données typées entre différentes parties de l'application,
comme les instances de services ou de configurations, tout en
résolvant les limitations de typage de l'état de Starlette/FastAPI.
"""

from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


class AppState(Generic[T]):
    """
    Classe pour représenter l'état partagé de l'application.
    Cette classe aide à résoudre les problèmes de typage avec
    l'état de l'application FastAPI/Starlette.
    """

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: T) -> None:
        """
        Définit une valeur dans l'état de l'application.

        Args:
            key: Clé d'accès.
            value: Valeur à stocker.
        """
        self._data[key] = value

    def get(self, key: str) -> Optional[T]:
        """
        Récupère une valeur depuis l'état de l'application.

        Args:
            key: Clé d'accès.

        Returns:
            La valeur associée à la clé ou None si la clé n'existe pas.
        """
        return self._data.get(key)

    def has(self, key: str) -> bool:
        """
        Vérifie si une clé existe dans l'état.

        Args:
            key: Clé à vérifier.

        Returns:
            True si la clé existe, False sinon.
        """
        return key in self._data
