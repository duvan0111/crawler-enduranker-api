"""
Contrôleur pour gérer les requêtes utilisateur.
"""

from fastapi import HTTPException
from typing import List, Dict
import os

from src.models.user_query_model import (
    UserQueryRequestModel,
    UserQueryResponseModel
)
from src.services.user_query_service_simple import get_user_query_service_simple


class UserQueryController:
    """Contrôleur pour gérer les opérations sur les requêtes utilisateur"""
    
    def __init__(self):
        """Initialise le contrôleur avec la configuration MongoDB"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
        self.user_query_service = get_user_query_service_simple(mongodb_url, mongodb_db)
    
    async def sauvegarder_requete(self, request: UserQueryRequestModel) -> UserQueryResponseModel:
        """
        Sauvegarde une requête utilisateur avec son embedding.
        
        Args:
            request: Requête contenant la question de l'utilisateur
            
        Returns:
            Réponse contenant les détails de la requête sauvegardée
        """
        try:
            response = await self.user_query_service.sauvegarder_requete(request.question)
            return response
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde: {str(e)}")
    
    async def obtenir_requetes_recentes(self, limite: int = 50) -> List[Dict]:
        """
        Obtient les requêtes utilisateur récentes.
        
        Args:
            limite: Nombre maximum de requêtes à retourner
            
        Returns:
            Liste des requêtes récentes
        """
        try:
            requetes = await self.user_query_service.obtenir_requetes_recentes(limite)
            return requetes
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")
    
    async def obtenir_statistiques(self) -> Dict:
        """
        Obtient les statistiques sur les requêtes utilisateur.
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        try:
            stats = await self.user_query_service.obtenir_statistiques_requetes()
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")


# Instance unique du contrôleur
user_query_controller = UserQueryController()
