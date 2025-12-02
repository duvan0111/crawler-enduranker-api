"""
Routes API pour les requêtes utilisateur.
"""

from fastapi import APIRouter, status, Query
from typing import List, Dict, Optional

from src.models.user_query_model import (
    UserQueryRequestModel,
    UserQueryResponseModel
)
from src.controllers.user_query_controller import user_query_controller

# Créer le routeur
router = APIRouter(
    prefix="/api/queries",
    tags=["User Queries"],
    responses={404: {"description": "Non trouvé"}},
)


@router.post("/save", response_model=UserQueryResponseModel, status_code=status.HTTP_201_CREATED)
async def sauvegarder_requete(request: UserQueryRequestModel):
    """
    Sauvegarde une requête utilisateur avec son embedding vectoriel.
    
    Cette route permet de stocker les questions des utilisateurs dans une collection
    dédiée avec génération automatique d'embeddings pour l'analyse sémantique.
    
    **Exemple de requête:**
    ```json
    {
        "question": "Comment apprendre le machine learning ?"
    }
    ```
    
    **Paramètres:**
    - **question**: Question de l'utilisateur (requis)
    
    **Retourne:**
    - ID de la requête sauvegardée
    - Confirmation de génération d'embedding
    - Langue détectée
    - Date de création
    """
    return await user_query_controller.sauvegarder_requete(request)


@router.get("/recent", response_model=List[Dict], status_code=status.HTTP_200_OK)
async def obtenir_requetes_recentes(
    limit: int = Query(50, description="Nombre maximum de requêtes", ge=1, le=200)
):
    """
    Obtient les requêtes utilisateur récentes.
    
    Cette route permet de récupérer les dernières questions posées par les utilisateurs,
    triées par date de création décroissante.
    
    **Paramètres de requête:**
    - **limit**: Nombre maximum de requêtes à retourner (défaut: 50)
    
    **Exemple:**
    `/api/queries/recent?limit=20`
    
    **Retourne:**
    - Liste des requêtes récentes avec métadonnées (sans embeddings pour optimiser)
    """
    return await user_query_controller.obtenir_requetes_recentes(limit)


@router.get("/stats", response_model=Dict, status_code=status.HTTP_200_OK)
async def obtenir_statistiques_requetes():
    """
    Obtient les statistiques détaillées sur les requêtes utilisateur.
    
    **Retourne:**
    - Nombre total de requêtes
    - Pourcentage avec embeddings générés
    - Répartition par langue
    - Évolution sur 7 derniers jours
    - Timestamp de génération
    """
    return await user_query_controller.obtenir_statistiques()
