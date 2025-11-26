"""
Routes API pour le crawling de ressources éducatives.
"""

from fastapi import APIRouter, status, Query
from typing import List, Dict, Optional

from src.models.crawler_model import (
    CrawlRequestModel,
    CrawlResponseModel,
    SearchRequestModel,
    RessourceEducativeModel
)
from src.controllers.crawler_controller import crawler_controller

# Créer le routeur
router = APIRouter(
    prefix="/api/crawler",
    tags=["Crawler"],
    responses={404: {"description": "Non trouvé"}},
)


@router.post("/collect", response_model=CrawlResponseModel, status_code=status.HTTP_200_OK)
async def collecter_ressources(request: CrawlRequestModel):
    """
    Lance la collecte de ressources éducatives basée sur la question de l'utilisateur.
    
    La route collecte des articles depuis différentes sources (Wikipedia, GitHub, Medium)
    et retourne la liste des articles trouvés.
    
    **Exemple de requête:**
    ```json
    {
        "question": "deep learning en éducation",
        "max_par_site": 15,
        "sources": ["wikipedia", "github", "medium"],
        "langues": ["fr", "en"]
    }
    ```
    
    **Paramètres:**
    - **question**: La question ou le terme de recherche de l'utilisateur (requis)
    - **max_par_site**: Nombre maximum de résultats par source (optionnel, défaut: 15)
    - **sources**: Liste des sources à utiliser (optionnel, défaut: toutes)
    - **langues**: Langues pour Wikipedia (optionnel, défaut: ['fr', 'en'])
    
    **Retourne:**
    - Liste des articles/ressources trouvées avec leurs métadonnées
    - Statistiques de la collecte (durée, nombre total, etc.)
    """
    return await crawler_controller.collecter_ressources(request)


@router.get("/search", response_model=List[RessourceEducativeModel], status_code=status.HTTP_200_OK)
async def rechercher_ressources(
    query: str = Query(..., description="Terme de recherche"),
    source: Optional[str] = Query(None, description="Filtrer par source"),
    langue: Optional[str] = Query(None, description="Filtrer par langue"),
    limit: int = Query(50, description="Nombre maximum de résultats", ge=1, le=200)
):
    """
    Recherche dans les ressources éducatives déjà collectées.
    
    Cette route permet de rechercher dans la base de données existante
    sans lancer une nouvelle collecte.
    
    **Paramètres de requête:**
    - **query**: Terme de recherche (requis)
    - **source**: Filtrer par source spécifique (optionnel)
    - **langue**: Filtrer par langue (optionnel)  
    - **limit**: Nombre maximum de résultats (optionnel, défaut: 50)
    
    **Exemple:**
    `/api/crawler/search?query=machine%20learning&source=wikipedia&limit=10`
    
    **Retourne:**
    - Liste des ressources correspondant aux critères de recherche
    """
    # Créer l'objet SearchRequestModel
    request = SearchRequestModel(
        question=query,
        source=source,
        langue=langue,
        limite=limit
    )
    return await crawler_controller.rechercher_ressources(request)


@router.get("/stats", response_model=Dict, status_code=status.HTTP_200_OK)
async def obtenir_statistiques():
    """
    Obtient les statistiques sur les ressources collectées.
    
    **Retourne:**
    - Nombre total de ressources
    - Statistiques par source
    - Statistiques par langue
    - Date de dernière mise à jour
    """
    return await crawler_controller.obtenir_statistiques()


@router.get("/sources", response_model=List[str], status_code=status.HTTP_200_OK)
async def obtenir_sources_disponibles():
    """
    Retourne la liste des sources disponibles pour la collecte.
    
    **Retourne:**
    - Liste des sources supportées (wikipedia, github, medium)
    """
    return ["wikipedia", "github", "medium"]
