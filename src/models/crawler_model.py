from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RessourceEducativeModel(BaseModel):
    """Modèle pour une ressource éducative collectée"""
    titre: str = Field(..., description="Titre de la ressource")
    url: str = Field(..., description="URL de la ressource")
    source: str = Field(..., description="Source de la ressource (wikipedia, github, medium)")
    langue: Optional[str] = Field(None, description="Langue de la ressource")
    auteur: Optional[str] = Field(None, description="Auteur de la ressource")
    date: Optional[str] = Field(None, description="Date de publication")
    texte: Optional[str] = Field(None, description="Contenu textuel de la ressource")
    popularite: Optional[int] = Field(None, description="Score de popularité")
    type_ressource: Optional[str] = Field(None, description="Type de ressource")
    mots_cles: Optional[List[str]] = Field(default_factory=list, description="Mots-clés associés")
    requete_originale: Optional[str] = Field(None, description="Requête de recherche originale")
    date_collecte: Optional[datetime] = Field(None, description="Date de collecte")

    class Config:
        json_schema_extra = {
            "example": {
                "titre": "Introduction au Machine Learning",
                "url": "https://example.com/ml-intro",
                "source": "wikipedia",
                "langue": "fr",
                "auteur": "John Doe",
                "date": "2024-01-15",
                "texte": "Le machine learning est...",
                "popularite": 150,
                "type_ressource": "article",
                "mots_cles": ["machine learning", "IA", "éducation"],
                "requete_originale": "machine learning",
                "date_collecte": "2024-01-20T10:30:00"
            }
        }


class CrawlRequestModel(BaseModel):
    """Modèle pour la requête de crawling"""
    question: str = Field(..., min_length=1, description="Question ou terme de recherche")
    max_par_site: Optional[int] = Field(default=15, ge=1, le=50, description="Nombre maximum de résultats par site")
    sources: Optional[List[str]] = Field(default=None, description="Sources à utiliser (wikipedia, github, medium)")
    langues: Optional[List[str]] = Field(default=None, description="Langues pour Wikipedia (ex: ['fr', 'en'])")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "deep learning en éducation",
                "max_par_site": 15,
                "sources": ["wikipedia", "github", "medium"],
                "langues": ["fr", "en"]
            }
        }


class CrawlResponseModel(BaseModel):
    """Modèle pour la réponse de crawling"""
    requete: str
    total_collecte: int
    duree_collecte_secondes: float
    sources_utilisees: List[str]
    resultats: List[RessourceEducativeModel]
    erreurs: Optional[List[str]] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "requete": "machine learning",
                "total_collecte": 25,
                "duree_collecte_secondes": 12.5,
                "sources_utilisees": ["wikipedia", "github"],
                "resultats": [],
                "erreurs": []
            }
        }


class SearchRequestModel(BaseModel):
    """Modèle pour rechercher dans les ressources existantes"""
    question: str = Field(..., min_length=1, description="Terme de recherche")
    source: Optional[str] = Field(None, description="Filtrer par source")
    langue: Optional[str] = Field(None, description="Filtrer par langue")
    limite: Optional[int] = Field(default=50, ge=1, le=200, description="Nombre maximum de résultats")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "machine learning",
                "source": "wikipedia",
                "langue": "fr",
                "limite": 50
            }
        }
