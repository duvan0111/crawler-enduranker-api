"""
Modèles pour le workflow global de traitement des requêtes.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class WorkflowRequestModel(BaseModel):
    """Modèle pour la requête du workflow global"""
    question: str = Field(..., min_length=1, description="Question de l'utilisateur")
    max_par_site: Optional[int] = Field(default=15, ge=1, le=50, description="Nombre maximum de résultats par site pour le crawling")
    sources: Optional[List[str]] = Field(default=["wikipedia", "github", "medium"], description="Sources à crawler")
    langues: Optional[List[str]] = Field(default=["fr", "en"], description="Langues pour Wikipedia")
    top_k_faiss: Optional[int] = Field(default=50, ge=1, le=200, description="Nombre de résultats FAISS avant re-ranking")
    top_k_final: Optional[int] = Field(default=10, ge=1, le=50, description="Nombre de résultats finaux après re-ranking")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Comment apprendre le machine learning ?",
                "max_par_site": 15,
                "sources": ["wikipedia", "github", "medium"],
                "langues": ["fr", "en"],
                "top_k_faiss": 50,
                "top_k_final": 10
            }
        }


class RessourceResultatModel(BaseModel):
    """Modèle pour une ressource dans les résultats finaux"""
    titre: str = Field(..., description="Titre de la ressource")
    url: str = Field(..., description="URL de la ressource")
    auteur: Optional[str] = Field(None, description="Auteur de la ressource")
    date: Optional[str] = Field(None, description="Date de publication")
    resume: Optional[str] = Field(None, description="Résumé ou extrait de la ressource")
    score_faiss: Optional[float] = Field(None, description="Score de similarité FAISS")
    score_reranking: Optional[float] = Field(None, description="Score du cross-encoder")
    score_final: float = Field(..., description="Score final combiné")
    mots_cles: List[str] = Field(default_factory=list, description="Mots-clés de la ressource")
    source: str = Field(..., description="Source de la ressource")
    id_inference: str = Field(..., description="ID de l'inférence MongoDB")
    
    class Config:
        json_schema_extra = {
            "example": {
                "titre": "Introduction au Machine Learning",
                "url": "https://example.com/ml-intro",
                "auteur": "John Doe",
                "date": "2024-01-15",
                "resume": "Le machine learning est une branche de l'intelligence artificielle...",
                "score_faiss": 0.85,
                "score_reranking": 0.92,
                "score_final": 0.89,
                "mots_cles": ["machine learning", "IA", "éducation"],
                "source": "wikipedia",
                "id_inference": "507f1f77bcf86cd799439011"
            }
        }


class WorkflowResponseModel(BaseModel):
    """Modèle pour la réponse du workflow global"""
    question: str = Field(..., description="Question de l'utilisateur")
    id_requete: str = Field(..., description="ID de la requête sauvegardée")
    total_crawle: int = Field(..., description="Nombre total de ressources crawlées")
    total_resultats_faiss: int = Field(..., description="Nombre de résultats de la recherche FAISS")
    total_resultats_final: int = Field(..., description="Nombre de résultats finaux")
    duree_crawl_secondes: float = Field(..., description="Durée du crawling")
    duree_recherche_secondes: float = Field(..., description="Durée de la recherche")
    duree_reranking_secondes: float = Field(..., description="Durée du re-ranking")
    duree_totale_secondes: float = Field(..., description="Durée totale du traitement")
    resultats: List[RessourceResultatModel] = Field(..., description="Top 10 des meilleures ressources")
    sources_crawlees: List[str] = Field(..., description="Sources qui ont été crawlées")
    erreurs: Optional[List[str]] = Field(default_factory=list, description="Erreurs éventuelles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Comment apprendre le machine learning ?",
                "id_requete": "507f1f77bcf86cd799439011",
                "total_crawle": 45,
                "total_resultats_faiss": 50,
                "total_resultats_final": 10,
                "duree_crawl_secondes": 12.5,
                "duree_recherche_secondes": 0.3,
                "duree_reranking_secondes": 1.2,
                "duree_totale_secondes": 14.0,
                "resultats": [],
                "sources_crawlees": ["wikipedia", "github", "medium"],
                "erreurs": []
            }
        }
