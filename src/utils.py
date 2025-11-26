"""
Utilitaires pour MongoDB
Fonctions helper pour gérer les opérations courantes avec MongoDB
"""

from bson import ObjectId
from typing import Optional, Dict, Any


def object_id_to_str(obj_id: ObjectId) -> str:
    """Convertir un ObjectId en string"""
    return str(obj_id)


def str_to_object_id(id_str: str) -> Optional[ObjectId]:
    """Convertir une string en ObjectId"""
    if not ObjectId.is_valid(id_str):
        return None
    return ObjectId(id_str)


def prepare_document_for_response(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Préparer un document MongoDB pour la réponse API
    Convertit les ObjectId en strings
    """
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document


def prepare_documents_for_response(documents: list) -> list:
    """
    Préparer une liste de documents MongoDB pour la réponse API
    """
    return [prepare_document_for_response(doc) for doc in documents]


def remove_none_values(data: dict) -> dict:
    """
    Supprimer les valeurs None d'un dictionnaire
    Utile pour les mises à jour partielles
    """
    return {k: v for k, v in data.items() if v is not None}
