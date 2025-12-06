"""
Contrôleur pour gérer les requêtes liées au crawling de ressources éducatives.
"""

from fastapi import HTTPException
from typing import List, Dict
import os

from src.models.crawler_model import (
    CrawlRequestModel,
    CrawlResponseModel,
    SearchRequestModel,
    RessourceEducativeModel
)
from src.services.crawler_service import get_simple_crawler_service


class CrawlerController:
    """Contrôleur pour gérer les opérations de crawling"""
    
    def __init__(self):
        """Initialise le contrôleur avec la configuration MongoDB"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
        self.crawler_service = get_simple_crawler_service(mongodb_url, mongodb_db)
    
    async def collecter_ressources(self, request: CrawlRequestModel) -> CrawlResponseModel:
        """
        Lance la collecte de ressources éducatives basée sur la question de l'utilisateur.
        
        Args:
            request: Requête de crawling contenant la question et les paramètres
            
        Returns:
            Réponse contenant les résultats de la collecte
        """
        try:
            # Lancer la collecte
            resultats = await self.crawler_service.collecter_ressources(
                question=request.question,
                max_par_site=request.max_par_site,
                sources=request.sources,
                langues=request.langues
            )
            
            # Construire la réponse
            response = CrawlResponseModel(
                requete=resultats['requete'],
                total_collecte=resultats['total_collecte'],
                duree_collecte_secondes=resultats['duree_collecte_secondes'],
                sources_utilisees=resultats['sources_utilisees'],
                resultats=resultats.get('ressources', []),
                erreurs=resultats.get('erreurs', [])
            )
            
            return response
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la collecte: {str(e)}")
    
    async def rechercher_ressources(self, request: SearchRequestModel) -> List[RessourceEducativeModel]:
        """
        Recherche dans les ressources déjà collectées.
        
        Args:
            request: Requête de recherche
            
        Returns:
            Liste des ressources trouvées
        """
        try:
            ressources = await self.crawler_service.rechercher_ressources(
                question=request.question,
                source=request.source,
                langue=request.langue,
                limite=request.limite
            )
            
            return ressources
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche: {str(e)}")
    
    async def obtenir_statistiques(self) -> Dict:
        """
        Obtient les statistiques sur les ressources collectées.
        
        Returns:
            Dictionnaire contenant les statistiques
        """
        try:
            stats = await self.crawler_service.obtenir_statistiques()
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques: {str(e)}")


# Instance unique du contrôleur
crawler_controller = CrawlerController()
