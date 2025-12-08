"""
Contrôleur pour gérer les opérations de re-ranking avec cross-encoder et feedbacks.
"""

from fastapi import HTTPException
from typing import Dict, Any
import os
import time
import numpy as np
import pickle

from src.models.reranking_model import (
    RerankingRequestModel,
    RerankingResponseModel,
    RerankingResultModel,
    FeedbackRequestModel,
    FineTuningStatsModel
)
from src.services.nlp_service import get_nlp_service
from src.services.reranking_service import get_reranking_service


class RerankingController:
    """Contrôleur pour gérer les opérations de re-ranking et feedbacks"""
    
    def __init__(self):
        """Initialise le contrôleur avec les services nécessaires"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
        model_name = os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        model_path = os.getenv("CROSS_ENCODER_PATH", "models/cross_encoder")
        
        self.nlp_service = get_nlp_service(mongodb_url, mongodb_db)
        self.reranking_service = get_reranking_service(mongodb_url, mongodb_db, model_name, model_path)
    
    async def recherche_avec_reranking(self, request: RerankingRequestModel) -> RerankingResponseModel:
        """
        Effectue une recherche sémantique avec re-ranking par cross-encoder.
        
        Pipeline:
        1. Sauvegarde de la requête utilisateur
        2. Recherche FAISS pour récupérer top_k_faiss candidats
        3. Re-ranking avec cross-encoder pour affiner le classement
        4. Sauvegarde des inférences dans MongoDB
        5. Retour des top_k_final meilleurs résultats
        
        Args:
            request: Requête de re-ranking contenant la question et les paramètres
            
        Returns:
            Réponse contenant les résultats re-rankés
        """
        try:
            start_time = time.time()
            
            # Étape 0: Sauvegarder la requête utilisateur et obtenir son ID
            from src.services.user_query_service import get_user_query_service
            user_query_service = get_user_query_service(
                os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
                os.getenv("MONGODB_DB_NAME", "eduranker_db")
            )
            query_response = await user_query_service.sauvegarder_requete(request.question)
            user_query_id = query_response.id  # Correction: utiliser 'id' au lieu de 'query_id'
            
            # Étape 1: Recherche FAISS
            resultats_faiss = await self.nlp_service.recherche_et_recuperer_ressources(
                request.question,
                top_k=request.top_k_faiss
            )
            
            if not resultats_faiss:
                return RerankingResponseModel(
                    question=request.question,
                    nb_resultats_faiss=0,
                    nb_resultats_finaux=0,
                    reranking_applique=False,
                    resultats=[],
                    duree_recherche_ms=0
                )
            
            # Étape 2: Re-ranking (si activé)
            if request.use_reranker:
                resultats_finaux = await self.reranking_service.reranker_resultats(
                    request.question,
                    resultats_faiss,
                    top_k=request.top_k_final
                )
                reranking_applique = True
            else:
                resultats_finaux = resultats_faiss[:request.top_k_final]
                reranking_applique = False
                # Ajouter le rang
                for i, res in enumerate(resultats_finaux, 1):
                    res['rank'] = i
                    res['final_score'] = res.get('score_similarite', 0.0)
            
            # Étape 3: Formater les résultats et sauvegarder les inférences
            resultats_formates = []
            for res in resultats_finaux:
                # Sauvegarder l'inférence dans MongoDB
                inference_result = await self.reranking_service.sauvegarder_inference(
                    user_query_id=user_query_id,
                    resource_id=res.get('_id', ''),
                    faiss_score=res.get('faiss_score', res.get('score_similarite', 0.0)),
                    reranking_score=res.get('reranking_score'),
                    final_score=res.get('final_score', 0.0),
                    rank=res.get('rank', 0),
                    session_id=request.session_id
                )
                
                # Formater le résultat avec l'ID de l'inférence
                result = RerankingResultModel(
                    inference_id=inference_result.get('inference_id') if inference_result.get('status') == 'success' else None,
                    resource_id=res.get('_id', ''),
                    titre=res.get('titre', 'Sans titre'),
                    url=res.get('url', ''),
                    source=res.get('source', ''),
                    texte=res.get('texte', '')[:500] if res.get('texte') else None,
                    faiss_score=res.get('faiss_score', res.get('score_similarite', 0.0)),
                    reranking_score=res.get('reranking_score'),
                    final_score=res.get('final_score', 0.0),
                    rank=res.get('rank', 0)
                )
                resultats_formates.append(result)
            
            duree_ms = (time.time() - start_time) * 1000
            
            return RerankingResponseModel(
                question=request.question,
                nb_resultats_faiss=len(resultats_faiss),
                nb_resultats_finaux=len(resultats_formates),
                reranking_applique=reranking_applique,
                resultats=resultats_formates,
                duree_recherche_ms=round(duree_ms, 2)
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur recherche avec re-ranking: {str(e)}"
            )
    
    async def soumettre_feedback(self, feedback: FeedbackRequestModel) -> Dict[str, Any]:
        """
        Met à jour le feedback d'une inférence.
        Ces feedbacks sont utilisés pour le fine-tuning du cross-encoder.
        
        Args:
            feedback: Modèle contenant l'ID de l'inférence et le type de feedback
            
        Returns:
            Résultat de l'enregistrement du feedback
        """
        try:
            result = await self.reranking_service.sauvegarder_feedback(
                inference_id=feedback.inference_id,
                feedback_type=feedback.feedback_type
            )
            
            if result.get("status") == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur sauvegarde feedback: {str(e)}"
            )
    
    async def obtenir_statistiques_feedback(self) -> FineTuningStatsModel:
        """
        Récupère les statistiques des feedbacks utilisateurs.
        
        Returns:
            Statistiques des feedbacks
        """
        try:
            stats = await self.reranking_service.obtenir_statistiques_feedback()
            return stats
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur récupération statistiques: {str(e)}"
            )
    
    async def lancer_fine_tuning(
        self,
        num_epochs: int,
        batch_size: int,
        learning_rate: float
    ) -> Dict[str, Any]:
        """
        Lance le fine-tuning du cross-encoder sur les feedbacks utilisateurs.
        
        ⚠️  ATTENTION: Cette opération peut prendre plusieurs minutes
        
        Args:
            num_epochs: Nombre d'époques d'entraînement
            batch_size: Taille des batchs
            learning_rate: Taux d'apprentissage
            
        Returns:
            Résultat du fine-tuning
        """
        try:
            # Vérifier qu'il y a assez de données
            stats = await self.reranking_service.obtenir_statistiques_feedback()
            if stats.nb_training_pairs < 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"Pas assez de feedbacks pour le fine-tuning. "
                           f"Actuel: {stats.nb_training_pairs}, minimum: 10"
                )
            
            result = await self.reranking_service.fine_tuner_modele(
                num_epochs=num_epochs,
                batch_size=batch_size,
                learning_rate=learning_rate
            )
            
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["message"])
            
            return {
                "status": "success",
                "message": "Fine-tuning terminé avec succès",
                "details": result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur fine-tuning: {str(e)}"
            )
    
    def predire_score_pertinence(self, query: str, document: str) -> Dict[str, Any]:
        """
        Prédit le score de pertinence pour une paire (query, document).
        Utile pour tester le modèle cross-encoder.
        
        Args:
            query: Texte de la requête
            document: Texte du document
            
        Returns:
            Score de pertinence et interprétation
        """
        try:
            score = self.reranking_service.predict_score(query, document)
            
            # Normaliser avec sigmoïde pour avoir un score 0-1
            score_normalized = 1 / (1 + np.exp(-score))
            
            return {
                "status": "success",
                "query": query,
                "document": document[:100] + "..." if len(document) > 100 else document,
                "raw_score": float(score),
                "normalized_score": float(score_normalized),
                "interpretation": self._interpreter_score(score_normalized)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur prédiction: {str(e)}"
            )
    
    def obtenir_info_modele(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le modèle cross-encoder actuellement chargé.
        
        Returns:
            Informations sur le modèle
        """
        try:
            info = {
                "base_model": self.reranking_service.base_model_name,
                "model_path": self.reranking_service.model_path,
                "is_finetuned": os.path.exists(
                    os.path.join(self.reranking_service.model_path, "config.json")
                )
            }
            
            # Charger les métadonnées si disponibles
            metadata_path = os.path.join(self.reranking_service.model_path, "metadata.pkl")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    info["metadata"] = metadata
            
            return {
                "status": "success",
                "info": info
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur info modèle: {str(e)}"
            )
    
    async def recuperer_inferences(self, user_query_id: str) -> Dict[str, Any]:
        """
        Récupère toutes les inférences pour une requête utilisateur.
        
        Args:
            user_query_id: ID de la requête utilisateur
            
        Returns:
            Liste des inférences avec scores et feedbacks
        """
        try:
            inferences = await self.reranking_service.recuperer_inferences(user_query_id)
            
            return {
                "status": "success",
                "user_query_id": user_query_id,
                "nb_inferences": len(inferences),
                "inferences": inferences
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erreur récupération inférences: {str(e)}"
            )
    
    @staticmethod
    def _interpreter_score(score: float) -> str:
        """
        Interprète un score de pertinence.
        
        Args:
            score: Score normalisé entre 0 et 1
            
        Returns:
            Interprétation textuelle du score
        """
        if score >= 0.8:
            return "Très pertinent"
        elif score >= 0.6:
            return "Pertinent"
        elif score >= 0.4:
            return "Moyennement pertinent"
        elif score >= 0.2:
            return "Peu pertinent"
        else:
            return "Non pertinent"
