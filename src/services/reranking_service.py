"""
Service de Re-ranking avec Cross-Encoder pour affiner le classement des résultats FAISS.
Ce service utilise un modèle BERT cross-encoder qui peut être fine-tuné sur les feedbacks utilisateurs.
"""

import logging
import pickle
import os
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import pymongo
from datetime import datetime
from sentence_transformers import CrossEncoder
import torch

from src.models.reranking_model import (
    UserFeedbackModel,
    TrainingPairModel,
    FineTuningStatsModel,
    InferenceModel
)

logger = logging.getLogger(__name__)


class RerankingService:
    """Service pour le re-ranking avec cross-encoder et fine-tuning"""
    
    def __init__(
        self, 
        mongodb_url: str, 
        mongodb_db: str, 
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        model_path: str = "models/cross_encoder"
    ):
        """
        Initialise le service de re-ranking
        
        Args:
            mongodb_url: URL de connexion MongoDB
            mongodb_db: Nom de la base de données
            model_name: Nom du modèle cross-encoder de base
            model_path: Chemin pour sauvegarder le modèle fine-tuné
        """
        self.mongodb_url = mongodb_url
        self.mongodb_db = mongodb_db
        self.feedback_collection = "user_feedbacks"
        self.inference_collection = "inference"
        self.model_path = model_path
        self.base_model_name = model_name
        
        # Créer le dossier pour le modèle s'il n'existe pas
        Path(model_path).mkdir(parents=True, exist_ok=True)
        
        # Charger le cross-encoder
        self._charger_modele()
        
    def _charger_modele(self):
        """Charge le modèle cross-encoder (fine-tuné ou de base)"""
        try:
            # Essayer de charger un modèle fine-tuné
            if os.path.exists(os.path.join(self.model_path, "config.json")):
                logger.info(f"📥 Chargement du modèle fine-tuné depuis {self.model_path}...")
                self.cross_encoder = CrossEncoder(self.model_path)
                logger.info("✅ Modèle fine-tuné chargé avec succès")
            else:
                # Charger le modèle de base
                logger.info(f"📥 Chargement du modèle de base {self.base_model_name}...")
                self.cross_encoder = CrossEncoder(self.base_model_name)
                logger.info("✅ Modèle de base chargé avec succès")
                
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            logger.warning("⚠️  Le modèle cross-encoder n'a pas pu être chargé.")
            logger.warning("⚠️  Le service fonctionnera en mode dégradé (sans re-ranking).")
            logger.warning("⚠️  Solutions possibles :")
            logger.warning("    1. Augmenter le timeout : export HF_HUB_DOWNLOAD_TIMEOUT=600")
            logger.warning("    2. Télécharger le modèle manuellement : huggingface-cli download cross-encoder/ms-marco-MiniLM-L-6-v2")
            logger.warning("    3. Utiliser un miroir : export HF_ENDPOINT=https://hf-mirror.com")
            logger.warning("    4. Consulter TROUBLESHOOTING.md pour plus de solutions")
            self.cross_encoder = None  # Mode dégradé
    
    async def reranker_resultats(
        self,
        question: str,
        resultats_faiss: List[Dict],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Re-classe les résultats FAISS en utilisant le cross-encoder
        
        Args:
            question: Question de l'utilisateur
            resultats_faiss: Résultats de la recherche FAISS
            top_k: Nombre de résultats finaux à retourner
            
        Returns:
            Liste de résultats re-classés avec scores
        """
        if not resultats_faiss:
            return []
        
        # Mode dégradé : si le modèle n'est pas chargé, retourner les résultats FAISS sans re-ranking
        if self.cross_encoder is None:
            logger.warning("⚠️  Cross-encoder non disponible, retour des résultats FAISS sans re-ranking")
            resultats_tries = resultats_faiss[:top_k]
            for i, res in enumerate(resultats_tries, 1):
                res['rank'] = i
                res['faiss_score'] = res.get('score_similarite', 0.0)
                res['reranking_score'] = None
                res['final_score'] = res['faiss_score']
            return resultats_tries
        
        try:
            logger.info(f"🔄 Re-ranking de {len(resultats_faiss)} résultats avec cross-encoder...")
            
            # Préparer les paires (question, document)
            paires = []
            for res in resultats_faiss:
                # Créer un texte représentatif du document
                doc_text = self._creer_texte_document(res)
                paires.append([question, doc_text])
            
            # Prédire les scores avec le cross-encoder
            scores = self.cross_encoder.predict(paires, show_progress_bar=False)
            
            # Ajouter les scores aux résultats
            for i, res in enumerate(resultats_faiss):
                res['reranking_score'] = float(scores[i])
                res['faiss_score'] = res.get('score_similarite', 0.0)
                # Score final combiné (moyenne pondérée)
                res['final_score'] = self._calculer_score_final(
                    res['faiss_score'], 
                    res['reranking_score']
                )
            
            # Trier par score final décroissant
            resultats_tries = sorted(
                resultats_faiss, 
                key=lambda x: x['final_score'], 
                reverse=True
            )
            
            # Retourner les top_k meilleurs
            resultats_finaux = resultats_tries[:top_k]
            
            # Ajouter le rang
            for i, res in enumerate(resultats_finaux, 1):
                res['rank'] = i
            
            logger.info(f"✅ Re-ranking terminé: {len(resultats_finaux)} résultats retournés")
            return resultats_finaux
            
        except Exception as e:
            logger.error(f"❌ Erreur re-ranking: {e}")
            # En cas d'erreur, retourner les résultats FAISS originaux
            return resultats_faiss[:top_k]
    
    def _creer_texte_document(self, ressource: Dict) -> str:
        """
        Crée un texte représentatif du document pour le cross-encoder
        
        Args:
            ressource: Dictionnaire de la ressource
            
        Returns:
            Texte concaténé (titre + extrait de texte)
        """
        titre = ressource.get('titre', '')
        texte = ressource.get('texte', '')
        
        # Limiter la longueur du texte pour le cross-encoder (max 512 tokens)
        # Approximation: 1 token ≈ 4 caractères
        max_chars = 1500
        
        if texte and len(texte) > max_chars:
            texte = texte[:max_chars] + "..."
        
        # Combiner titre et texte
        doc_text = f"{titre}. {texte}" if titre and texte else titre or texte
        
        return doc_text
    
    def _calculer_score_final(
        self, 
        faiss_score: float, 
        reranking_score: float,
        alpha: float = 0.3
    ) -> float:
        """
        Calcule le score final combiné
        
        Args:
            faiss_score: Score de similarité FAISS (0-1)
            reranking_score: Score du cross-encoder (-inf, +inf, typiquement -5 à 5)
            alpha: Poids pour FAISS (1-alpha pour reranking)
            
        Returns:
            Score final combiné
        """
        # Normaliser le score de reranking avec sigmoïde
        reranking_norm = 1 / (1 + np.exp(-reranking_score))
        
        # Combiner les scores
        final_score = alpha * faiss_score + (1 - alpha) * reranking_norm
        
        return float(final_score)
    
    async def sauvegarder_inference(
        self,
        user_query_id: str,
        resource_id: str,
        faiss_score: float,
        reranking_score: Optional[float],
        final_score: float,
        rank: int,
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Sauvegarde une inférence (recommandation) dans MongoDB
        
        Args:
            user_query_id: ID de la requête utilisateur
            resource_id: ID de la ressource recommandée
            faiss_score: Score FAISS
            reranking_score: Score du cross-encoder (peut être None)
            final_score: Score final combiné
            rank: Position dans le classement
            session_id: ID de session optionnel
            
        Returns:
            Dictionnaire avec le statut
        """
        try:
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            inference_col = db[self.inference_collection]
            
            # Créer l'inférence
            inference = {
                "user_query_id": user_query_id,
                "resource_id": resource_id,
                "faiss_score": faiss_score,
                "reranking_score": reranking_score,
                "final_score": final_score,
                "rank": rank,
                "feedback": None,  # Initialement à null
                "date_inference": datetime.now(),
                "session_id": session_id,
                "metadata": {}
            }
            
            # Sauvegarder dans MongoDB
            result = inference_col.insert_one(inference)
            
            client.close()
            
            logger.debug(f"💾 Inférence sauvegardée: rank {rank} pour requête {user_query_id}")
            
            return {
                "status": "success",
                "inference_id": str(result.inserted_id)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde inférence: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def sauvegarder_feedback(
        self,
        inference_id: str,
        feedback_type: str
    ) -> Dict:
        """
        Met à jour le feedback d'une inférence
        
        Args:
            inference_id: ID de l'inférence
            feedback_type: Type de feedback (like, dislike, click, view)
            
        Returns:
            Dictionnaire avec le statut
        """
        try:
            from bson import ObjectId
            
            # Se connecter à MongoDB
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            inference_col = db[self.inference_collection]
            
            # Vérifier que l'inférence existe
            inference = inference_col.find_one({"_id": ObjectId(inference_id)})
            
            if not inference:
                client.close()
                return {
                    "status": "error",
                    "message": f"Inférence {inference_id} introuvable"
                }
            
            # Mettre à jour le feedback dans l'inférence
            result = inference_col.update_one(
                {"_id": ObjectId(inference_id)},
                {
                    "$set": {
                        "feedback": feedback_type,
                        "date_feedback": datetime.now()
                    }
                }
            )
            
            # Sauvegarder aussi dans la collection user_feedbacks pour historique
            # feedback_col = db[self.feedback_collection]
            # feedback_doc = {
            #     "inference_id": inference_id,
            #     "user_query_id": inference.get("user_query_id"),
            #     "resource_id": inference.get("resource_id"),
            #     "feedback_type": feedback_type,
            #     "relevance_score": 1.0 if feedback_type == "like" else 0.0 if feedback_type == "dislike" else 0.5,
            #     "session_id": inference.get("session_id"),
            #     "date_feedback": datetime.now(),
            #     "metadata": {}
            # }
            # feedback_result = feedback_col.insert_one(feedback_doc)
            
            client.close()
            
            if result.modified_count > 0:
                logger.info(f"💾 Feedback '{feedback_type}' sauvegardé pour inférence {inference_id}")
                return {
                    "status": "success",
                    "inference_id": inference_id,
                    # "feedback_id": str(feedback_result.inserted_id),
                    "message": "Feedback enregistré avec succès"
                }
            else:
                return {
                    "status": "error",
                    "message": "Aucune modification effectuée"
                }
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde feedback: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def recuperer_donnees_entrainement(self) -> List[TrainingPairModel]:
        """
        Récupère les paires d'entraînement depuis les feedbacks
        
        Returns:
            Liste de paires (query, document, label)
        """
        try:
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            feedback_col = db[self.feedback_collection]
            
            # Récupérer tous les feedbacks avec like/dislike
            feedbacks = list(feedback_col.find({
                "feedback_type": {"$in": ["like", "dislike"]}
            }))
            
            client.close()
            
            # Créer les paires d'entraînement
            training_pairs = []
            for fb in feedbacks:
                pair = TrainingPairModel(
                    query_text=fb.get("query_text", ""),
                    document_text=fb.get("resource_title", "") + ". " + fb.get("resource_text", ""),
                    label=fb.get("relevance_score", 0.5)
                )
                training_pairs.append(pair)
            
            logger.info(f"📊 {len(training_pairs)} paires d'entraînement récupérées")
            return training_pairs
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération données: {e}")
            return []
    
    async def fine_tuner_modele(
        self,
        num_epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5
    ) -> Dict:
        """
        Fine-tune le modèle cross-encoder sur les feedbacks utilisateurs
        
        Args:
            num_epochs: Nombre d'époques d'entraînement
            batch_size: Taille des batchs
            learning_rate: Taux d'apprentissage
            
        Returns:
            Dictionnaire avec les statistiques d'entraînement
        """
        logger.info("🎓 Début du fine-tuning du cross-encoder...")
        
        try:
            # Récupérer les données d'entraînement
            training_pairs = await self.recuperer_donnees_entrainement()
            
            if len(training_pairs) < 10:
                return {
                    "status": "error",
                    "message": f"Pas assez de données ({len(training_pairs)} paires). Minimum 10 requis."
                }
            
            # Préparer les données pour sentence-transformers
            train_samples = []
            for pair in training_pairs:
                train_samples.append({
                    'texts': [pair.query_text, pair.document_text],
                    'label': pair.label
                })
            
            # Importer les modules nécessaires
            from sentence_transformers import InputExample
            from torch.utils.data import DataLoader
            
            # Créer les InputExamples
            train_examples = [
                InputExample(texts=sample['texts'], label=sample['label'])
                for sample in train_samples
            ]
            
            # Créer le DataLoader
            train_dataloader = DataLoader(
                train_examples, 
                shuffle=True, 
                batch_size=batch_size
            )
            
            # Configuration de l'entraînement
            warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)
            
            logger.info(f"📚 Entraînement sur {len(train_examples)} exemples...")
            logger.info(f"   Epochs: {num_epochs}, Batch size: {batch_size}")
            
            # Fine-tuning
            self.cross_encoder.fit(
                train_dataloader=train_dataloader,
                epochs=num_epochs,
                warmup_steps=warmup_steps,
                output_path=self.model_path,
                show_progress_bar=True
            )
            
            # Sauvegarder les métadonnées
            metadata = {
                "model_version": f"finetuned_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "base_model": self.base_model_name,
                "num_training_samples": len(train_examples),
                "num_epochs": num_epochs,
                "batch_size": batch_size,
                "learning_rate": learning_rate,
                "training_date": datetime.now().isoformat()
            }
            
            with open(os.path.join(self.model_path, "metadata.pkl"), 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"✅ Fine-tuning terminé! Modèle sauvegardé dans {self.model_path}")
            
            # Recharger le modèle fine-tuné
            self._charger_modele()
            
            return {
                "status": "success",
                "num_training_samples": len(train_examples),
                "num_epochs": num_epochs,
                "model_path": self.model_path,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur fine-tuning: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def obtenir_statistiques_feedback(self) -> FineTuningStatsModel:
        """
        Retourne les statistiques des feedbacks pour le fine-tuning
        
        Returns:
            Statistiques des feedbacks
        """
        try:
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            feedback_col = db[self.feedback_collection]
            
            # Compter les feedbacks
            total = feedback_col.count_documents({})
            likes = feedback_col.count_documents({"feedback_type": "like"})
            dislikes = feedback_col.count_documents({"feedback_type": "dislike"})
            
            client.close()
            
            # Charger les métadonnées du modèle
            metadata_path = os.path.join(self.model_path, "metadata.pkl")
            model_version = None
            last_training = None
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                    model_version = metadata.get("model_version")
                    training_date_str = metadata.get("training_date")
                    if training_date_str:
                        last_training = datetime.fromisoformat(training_date_str)
            
            stats = FineTuningStatsModel(
                nb_feedbacks_total=total,
                nb_likes=likes,
                nb_dislikes=dislikes,
                nb_training_pairs=likes + dislikes,
                model_version=model_version,
                last_training_date=last_training
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur statistiques: {e}")
            return FineTuningStatsModel(
                nb_feedbacks_total=0,
                nb_likes=0,
                nb_dislikes=0,
                nb_training_pairs=0
            )
    
    def predict_score(self, query: str, document: str) -> float:
        """
        Prédit le score de pertinence pour une paire (query, document)
        
        Args:
            query: Texte de la requête
            document: Texte du document
            
        Returns:
            Score de pertinence
        """
        try:
            score = self.cross_encoder.predict([[query, document]])[0]
            return float(score)
        except Exception as e:
            logger.error(f"❌ Erreur prédiction: {e}")
            return 0.0
    
    async def recuperer_inferences(self, user_query_id: str) -> List[Dict]:
        """
        Récupère toutes les inférences pour une requête utilisateur donnée
        
        Args:
            user_query_id: ID de la requête utilisateur
            
        Returns:
            Liste des inférences avec leurs scores et feedbacks
        """
        try:
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            inference_col = db[self.inference_collection]
            
            # Récupérer toutes les inférences pour cette requête
            inferences = list(inference_col.find(
                {"user_query_id": user_query_id}
            ).sort("rank", 1))  # Trier par rang croissant
            
            client.close()
            
            # Convertir les ObjectId en string
            for inf in inferences:
                inf['_id'] = str(inf['_id'])
            
            logger.info(f"📊 {len(inferences)} inférences récupérées pour requête {user_query_id}")
            return inferences
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération inférences: {e}")
            return []


# Instance singleton
_reranking_service_instance = None

def get_reranking_service(
    mongodb_url: str, 
    mongodb_db: str,
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    model_path: str = "models/cross_encoder"
) -> RerankingService:
    """
    Obtenir l'instance du service de re-ranking (singleton)
    
    Args:
        mongodb_url: URL de connexion MongoDB
        mongodb_db: Nom de la base de données
        model_name: Nom du modèle cross-encoder
        model_path: Chemin du modèle fine-tuné
        
    Returns:
        Instance du service de re-ranking
    """
    global _reranking_service_instance
    if _reranking_service_instance is None:
        _reranking_service_instance = RerankingService(
            mongodb_url, 
            mongodb_db, 
            model_name, 
            model_path
        )
    return _reranking_service_instance
