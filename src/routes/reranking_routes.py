"""
Routes pour le re-ranking avec cross-encoder et la gestion des feedbacks utilisateurs
"""

from fastapi import APIRouter, Query
from src.models.reranking_model import (
    RerankingRequestModel,
    RerankingResponseModel,
    FeedbackRequestModel,
    FineTuningStatsModel
)
from src.controllers.reranking_controller import RerankingController

router = APIRouter(prefix="/api/reranking", tags=["Re-ranking & Cross-Encoder"])
controller = RerankingController()


@router.post("/recherche-avec-reranking", response_model=RerankingResponseModel)
async def recherche_avec_reranking(request: RerankingRequestModel):
    """
    Recherche sémantique avec re-ranking par cross-encoder
    
    Pipeline:
    1. Recherche FAISS pour récupérer top_k_faiss candidats
    2. Re-ranking avec cross-encoder pour affiner le classement
    3. Retour des top_k_final meilleurs résultats
    """
    return await controller.recherche_avec_reranking(request)


@router.post("/feedback")
async def soumettre_feedback(feedback: FeedbackRequestModel):
    """
    Soumet un feedback utilisateur (like/dislike/click/view)
    Ces feedbacks sont utilisés pour le fine-tuning du cross-encoder
    """
    return await controller.soumettre_feedback(feedback)


@router.get("/statistiques-feedback", response_model=FineTuningStatsModel)
async def obtenir_statistiques_feedback():
    """
    Retourne les statistiques des feedbacks utilisateurs
    """
    return await controller.obtenir_statistiques_feedback()


@router.post("/fine-tune", deprecated=True)
async def lancer_fine_tuning(
    num_epochs: int = Query(default=3, ge=1, le=10, description="Nombre d'époques"),
    batch_size: int = Query(default=16, ge=4, le=64, description="Taille des batchs"),
    learning_rate: float = Query(default=2e-5, gt=0, description="Taux d'apprentissage")
):
    """
    ⚠️  DÉPRÉCIÉ : Utilisez le notebook Jupyter pour le fine-tuning
    
    Le fine-tuning se fait maintenant via le notebook :
    **notebooks/fine_tune_cross_encoder.ipynb**
    
    Ce notebook offre :
    - Visualisations détaillées des données
    - Métriques complètes (accuracy, F1, AUC)
    - Analyse comparative avant/après
    - Rapport d'entraînement automatique
    - Contrôle total des hyperparamètres
    
    **Instructions** :
    1. `pip install jupyter notebook`
    2. `cd notebooks && jupyter notebook`
    3. Ouvrir `fine_tune_cross_encoder.ipynb`
    4. Exécuter les cellules dans l'ordre
    
    Le modèle fine-tuné sera automatiquement chargé par l'API au redémarrage.
    """
    return await controller.lancer_fine_tuning(num_epochs, batch_size, learning_rate)


@router.post("/predict-score")
async def predire_score_pertinence(
    query: str = Query(..., description="Texte de la requête"),
    document: str = Query(..., description="Texte du document")
):
    """
    Prédit le score de pertinence pour une paire (query, document)
    Utile pour tester le modèle cross-encoder
    """
    return controller.predire_score_pertinence(query, document)


@router.get("/info-modele")
async def obtenir_info_modele():
    """
    Retourne les informations sur le modèle cross-encoder actuellement chargé
    """
    return controller.obtenir_info_modele()


@router.get("/inferences/{user_query_id}")
async def recuperer_inferences(user_query_id: str):
    """
    Récupère toutes les inférences (recommandations) pour une requête utilisateur
    
    Permet de voir tous les résultats recommandés avec leurs scores et feedbacks éventuels
    """
    return await controller.recuperer_inferences(user_query_id)
