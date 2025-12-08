"""
Modèles pour le re-ranking avec cross-encoder et le feedback utilisateur.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class UserFeedbackModel(BaseModel):
    """Modèle pour le feedback utilisateur sur une ressource"""
    user_query_id: str = Field(..., description="ID de la requête utilisateur")
    resource_id: str = Field(..., description="ID de la ressource éducative")
    query_text: str = Field(..., description="Texte de la requête originale")
    resource_title: str = Field(..., description="Titre de la ressource")
    resource_text: Optional[str] = Field(None, description="Extrait du texte de la ressource")
    feedback_type: Literal["like", "dislike", "click", "view"] = Field(..., description="Type de feedback")
    relevance_score: Optional[float] = Field(None, description="Score de pertinence (0-1)")
    session_id: Optional[str] = Field(None, description="ID de session utilisateur")
    date_feedback: datetime = Field(default_factory=datetime.now, description="Date du feedback")
    metadata: Optional[dict] = Field(default_factory=dict, description="Métadonnées supplémentaires")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_query_id": "507f1f77bcf86cd799439011",
                "resource_id": "507f1f77bcf86cd799439012",
                "query_text": "machine learning tutoriel",
                "resource_title": "Introduction au Machine Learning",
                "resource_text": "Le machine learning est une branche de l'IA...",
                "feedback_type": "like",
                "relevance_score": 0.95,
                "session_id": "session_123",
                "date_feedback": "2024-01-20T10:30:00"
            }
        }


class FeedbackRequestModel(BaseModel):
    """Modèle simplifié pour soumettre un feedback sur une inférence"""
    inference_id: str = Field(..., description="ID de l'inférence (recommandation)")
    feedback_type: Literal["like", "dislike", "click", "view"] = Field(..., description="Type de feedback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "inference_id": "507f1f77bcf86cd799439013",
                "feedback_type": "like"
            }
        }


class RerankingRequestModel(BaseModel):
    """Modèle pour une requête de re-ranking"""
    question: str = Field(..., min_length=1, description="Question de l'utilisateur")
    top_k_faiss: int = Field(default=50, ge=1, le=200, description="Nombre de résultats à récupérer via FAISS")
    top_k_final: int = Field(default=10, ge=1, le=50, description="Nombre de résultats finaux après re-ranking")
    use_reranker: bool = Field(default=True, description="Utiliser le cross-encoder pour le re-ranking")
    session_id: Optional[str] = Field(None, description="ID de session utilisateur")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "machine learning pour débutants",
                "top_k_faiss": 50,
                "top_k_final": 10,
                "use_reranker": True,
                "session_id": "session_123"
            }
        }


class RerankingResultModel(BaseModel):
    """Modèle pour un résultat après re-ranking"""
    inference_id: Optional[str] = Field(None, description="ID de l'inférence (pour feedback)")
    resource_id: str = Field(..., description="ID de la ressource")
    titre: str = Field(..., description="Titre de la ressource")
    url: str = Field(..., description="URL de la ressource")
    source: str = Field(..., description="Source de la ressource")
    texte: Optional[str] = Field(None, description="Extrait du texte")
    faiss_score: float = Field(..., description="Score FAISS (similarité cosine)")
    reranking_score: Optional[float] = Field(None, description="Score du cross-encoder")
    final_score: float = Field(..., description="Score final combiné")
    rank: int = Field(..., description="Position dans le classement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "inference_id": "507f1f77bcf86cd799439013",
                "resource_id": "507f1f77bcf86cd799439012",
                "titre": "Introduction au Machine Learning",
                "url": "https://example.com/ml-intro",
                "source": "wikipedia",
                "texte": "Le machine learning est...",
                "faiss_score": 0.85,
                "reranking_score": 0.92,
                "final_score": 0.89,
                "rank": 1
            }
        }


class RerankingResponseModel(BaseModel):
    """Modèle pour la réponse de re-ranking"""
    question: str = Field(..., description="Question originale")
    nb_resultats_faiss: int = Field(..., description="Nombre de résultats FAISS")
    nb_resultats_finaux: int = Field(..., description="Nombre de résultats finaux")
    reranking_applique: bool = Field(..., description="Re-ranking appliqué ou non")
    resultats: List[RerankingResultModel] = Field(..., description="Résultats classés")
    duree_recherche_ms: float = Field(..., description="Durée de la recherche en ms")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "machine learning",
                "nb_resultats_faiss": 50,
                "nb_resultats_finaux": 10,
                "reranking_applique": True,
                "resultats": [],
                "duree_recherche_ms": 150.5
            }
        }


class TrainingPairModel(BaseModel):
    """Modèle pour une paire d'entraînement (requête, document, label)"""
    query_text: str = Field(..., description="Texte de la requête")
    document_text: str = Field(..., description="Texte du document")
    label: float = Field(..., ge=0, le=1, description="Label de pertinence (0=non pertinent, 1=pertinent)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "machine learning tutoriel",
                "document_text": "Introduction complète au machine learning avec Python...",
                "label": 1.0
            }
        }


class FineTuningStatsModel(BaseModel):
    """Modèle pour les statistiques de fine-tuning"""
    nb_feedbacks_total: int = Field(..., description="Nombre total de feedbacks")
    nb_likes: int = Field(..., description="Nombre de likes")
    nb_dislikes: int = Field(..., description="Nombre de dislikes")
    nb_training_pairs: int = Field(..., description="Nombre de paires d'entraînement")
    model_version: Optional[str] = Field(None, description="Version du modèle")
    last_training_date: Optional[datetime] = Field(None, description="Date du dernier entraînement")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nb_feedbacks_total": 500,
                "nb_likes": 350,
                "nb_dislikes": 150,
                "nb_training_pairs": 500,
                "model_version": "v1.0",
                "last_training_date": "2024-01-20T10:30:00"
            }
        }


class InferenceModel(BaseModel):
    """Modèle pour stocker une inférence (recommandation) du système"""
    user_query_id: str = Field(..., description="ID de la requête utilisateur")
    resource_id: str = Field(..., description="ID de la ressource recommandée")
    faiss_score: float = Field(..., description="Score FAISS (similarité cosine)")
    reranking_score: Optional[float] = Field(None, description="Score du cross-encoder")
    final_score: float = Field(..., description="Score final combiné")
    rank: int = Field(..., description="Position dans le classement")
    feedback: Optional[str] = Field(None, description="Feedback utilisateur (like/dislike/click/view)")
    date_inference: datetime = Field(default_factory=datetime.now, description="Date de l'inférence")
    session_id: Optional[str] = Field(None, description="ID de session utilisateur")
    metadata: Optional[dict] = Field(default_factory=dict, description="Métadonnées supplémentaires")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_query_id": "507f1f77bcf86cd799439011",
                "resource_id": "507f1f77bcf86cd799439012",
                "faiss_score": 0.85,
                "reranking_score": 0.92,
                "final_score": 0.89,
                "rank": 1,
                "feedback": None,
                "date_inference": "2024-12-08T10:30:00",
                "session_id": "session_123"
            }
        }
