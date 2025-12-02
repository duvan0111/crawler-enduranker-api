"""
Modèle pour les requêtes utilisateur stockées dans MongoDB.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserQueryModel(BaseModel):
    """Modèle pour une requête utilisateur avec embedding"""
    question: str = Field(..., description="Question posée par l'utilisateur")
    date_creation: datetime = Field(default_factory=datetime.now, description="Date de création de la requête")
    embedding: Optional[List[float]] = Field(None, description="Représentation vectorielle de la question")
    langue_detectee: Optional[str] = Field(None, description="Langue détectée de la question")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Comment apprendre le machine learning ?",
                "date_creation": "2025-11-27T10:30:00",
                "embedding": [0.1, -0.2, 0.3, 0.4, -0.1],
                "langue_detectee": "fr"
            }
        }

class UserQueryRequestModel(BaseModel):
    """Modèle pour créer une nouvelle requête utilisateur"""
    question: str = Field(..., min_length=1, description="Question de l'utilisateur")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Comment débuter en deep learning ?"
            }
        }

class UserQueryResponseModel(BaseModel):
    """Modèle de réponse pour une requête utilisateur sauvegardée"""
    id: str = Field(..., description="ID de la requête dans MongoDB")
    question: str = Field(..., description="Question sauvegardée")
    date_creation: datetime = Field(..., description="Date de création")
    embedding_genere: bool = Field(..., description="Indique si l'embedding a été généré")
    langue_detectee: Optional[str] = Field(None, description="Langue détectée")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "question": "Comment débuter en deep learning ?",
                "date_creation": "2025-11-27T10:30:00",
                "embedding_genere": True,
                "langue_detectee": "fr"
            }
        }
