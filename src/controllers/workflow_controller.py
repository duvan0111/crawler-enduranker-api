"""
Contrôleur pour le workflow global de traitement des requêtes.
"""

import logging
import os
from src.services.workflow_service import get_workflow_service
from src.models.workflow_model import WorkflowRequestModel, WorkflowResponseModel

logger = logging.getLogger(__name__)


class WorkflowController:
    """Contrôleur pour orchestrer le workflow complet"""
    
    def __init__(self):
        """Initialise le contrôleur de workflow"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
        index_path = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
        
        self.workflow_service = get_workflow_service(
            mongodb_url=mongodb_url,
            mongodb_db=mongodb_db,
            index_path=index_path
        )
    
    async def traiter_requete(self, request: WorkflowRequestModel) -> WorkflowResponseModel:
        """
        Traite une requête complète de l'utilisateur
        
        Args:
            request: Paramètres de la requête
            
        Returns:
            Résultats du workflow complet
        """
        logger.info(f"📥 Nouvelle requête reçue: {request.question}")
        
        try:
            reponse = await self.workflow_service.traiter_requete_complete(request)
            logger.info(f"✅ Requête traitée avec succès: {reponse.total_resultats_final} résultats")
            return reponse
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement requête: {e}")
            raise


# Instance singleton du contrôleur
workflow_controller = WorkflowController()
