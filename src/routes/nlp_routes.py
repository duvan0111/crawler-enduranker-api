"""
Routes pour le service NLP et la recherche sémantique
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import os

from src.services.nlp_service import get_nlp_service
from src.models.crawler_model import RessourceEducativeModel

router = APIRouter(prefix="/api/nlp", tags=["NLP & Recherche Sémantique"])

# Récupérer l'instance du service NLP
def _get_nlp_service():
    """Helper pour obtenir le service NLP"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
    index_path = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
    return get_nlp_service(mongodb_url, mongodb_db, index_path)


@router.post("/recherche-semantique")
async def recherche_semantique(
    question: str = Query(..., description="Question pour la recherche sémantique"),
    top_k: int = Query(default=10, ge=1, le=100, description="Nombre de résultats à retourner")
):
    """
    Effectue une recherche sémantique dans les ressources éducatives
    en utilisant l'index FAISS
    """
    try:
        nlp_service = _get_nlp_service()
        
        # Effectuer la recherche sémantique et récupérer les ressources
        resultats = await nlp_service.recherche_et_recuperer_ressources(question, top_k)
        
        return {
            "status": "success",
            "question": question,
            "nb_resultats": len(resultats),
            "resultats": resultats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur recherche sémantique: {str(e)}")


@router.get("/statistiques-index")
async def obtenir_statistiques_index():
    """
    Retourne les statistiques de l'index FAISS
    """
    try:
        nlp_service = _get_nlp_service()
        stats = nlp_service.obtenir_statistiques_index()
        
        return {
            "status": "success",
            "statistiques": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récupération statistiques: {str(e)}")


@router.post("/reconstruire-index")
async def reconstruire_index():
    """
    Force la reconstruction de l'index FAISS depuis MongoDB
    (Utile pour la maintenance ou après une corruption)
    """
    try:
        nlp_service = _get_nlp_service()
        result = await nlp_service.reconstruire_index_depuis_bd()
        
        return {
            "status": "success",
            "resultat": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur reconstruction index: {str(e)}")


@router.post("/ajouter-ressources")
async def ajouter_ressources_index(
    resource_ids: List[str] = Query(..., description="Liste des IDs MongoDB des ressources à ajouter")
):
    """
    Ajoute des ressources spécifiques à l'index FAISS
    (Utilisé automatiquement après un crawl)
    """
    try:
        nlp_service = _get_nlp_service()
        result = await nlp_service.ajouter_ressources_a_index(resource_ids)
        
        return {
            "status": "success",
            "resultat": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ajout ressources: {str(e)}")


@router.post("/generer-embedding")
async def generer_embedding(
    texte: str = Query(..., description="Texte à vectoriser")
):
    """
    Génère un embedding pour un texte donné
    (Utile pour tester le modèle)
    """
    try:
        nlp_service = _get_nlp_service()
        embedding = nlp_service.generer_embedding(texte)
        
        if embedding is None:
            raise HTTPException(status_code=400, detail="Impossible de générer l'embedding")
        
        return {
            "status": "success",
            "texte": texte,
            "embedding_dimension": len(embedding),
            "embedding": embedding.tolist()[:10]  # Afficher seulement les 10 premières valeurs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur génération embedding: {str(e)}")
