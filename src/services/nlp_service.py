"""
Service NLP pour l'indexation et la recherche sémantique avec FAISS.
Ce service gère l'indexation des embeddings de ressources éducatives
et permet la recherche sémantique basée sur les questions utilisateur.
"""

import logging
import pickle
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import numpy as np
import faiss
import pymongo
from sentence_transformers import SentenceTransformer

from src.models.crawler_model import RessourceEducativeModel

logger = logging.getLogger(__name__)


class NLPService:
    """Service pour le traitement NLP et la recherche sémantique avec FAISS"""
    
    def __init__(self, mongodb_url: str, mongodb_db: str, index_path: str = "data/faiss_index"):
        """
        Initialise le service NLP
        
        Args:
            mongodb_url: URL de connexion MongoDB
            mongodb_db: Nom de la base de données
            index_path: Chemin pour sauvegarder l'index FAISS
        """
        self.mongodb_url = mongodb_url
        self.mongodb_db = mongodb_db
        self.mongodb_collection = "ressources_educatives"
        self.index_path = index_path
        
        # Créer le dossier pour l'index s'il n'existe pas
        Path(index_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Charger le modèle sentence-transformers
        logger.info("📥 Chargement du modèle sentence-transformers pour NLP Service...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.embedding_dimension = 384  # Dimension du modèle all-MiniLM-L6-v2
        logger.info(f"✅ Modèle NLP chargé ({self.embedding_dimension} dimensions)")
        
        # Initialiser l'index FAISS
        self.index = None
        self.resource_ids = []  # Liste des IDs MongoDB correspondant aux vecteurs
        
    def _creer_index_faiss(self) -> faiss.Index:
        """
        Crée un nouvel index FAISS optimisé pour la recherche sémantique
        
        Returns:
            Index FAISS configuré
        """
        # Utiliser IndexFlatIP pour la similarité cosine (Inner Product)
        # Note: les embeddings de sentence-transformers sont normalisés
        index = faiss.IndexFlatIP(self.embedding_dimension)
        logger.info(f"✅ Index FAISS créé (dimension: {self.embedding_dimension})")
        return index
    
    def generer_embedding(self, texte: str) -> Optional[np.ndarray]:
        """
        Génère un embedding pour un texte donné
        
        Args:
            texte: Texte à vectoriser
            
        Returns:
            Vecteur numpy normalisé ou None en cas d'erreur
        """
        if not texte or not texte.strip():
            return None
        
        try:
            # Générer l'embedding
            embedding = self.embedding_model.encode(
                texte.strip(), 
                normalize_embeddings=True,  # Normaliser pour la similarité cosine
                show_progress_bar=False
            )
            return embedding.astype('float32')
            
        except Exception as e:
            logger.error(f"❌ Erreur génération embedding: {e}")
            return None
    
    async def reconstruire_index_depuis_bd(self) -> Dict:
        """
        Reconstruit l'index FAISS à partir de tous les embeddings stockés dans MongoDB
        Cette fonction est appelée au démarrage de l'application
        
        Returns:
            Dictionnaire avec les statistiques de reconstruction
        """
        logger.info("🔄 Reconstruction de l'index FAISS depuis MongoDB...")
        
        try:
            # Se connecter à MongoDB
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            collection = db[self.mongodb_collection]
            
            # Récupérer toutes les ressources avec embeddings
            ressources = list(collection.find(
                {"embedding": {"$exists": True, "$ne": None}},
                {"_id": 1, "embedding": 1}
            ))
            
            client.close()
            
            if not ressources:
                logger.warning("⚠️ Aucun embedding trouvé dans la base de données")
                # Créer un index vide
                self.index = self._creer_index_faiss()
                self.resource_ids = []
                self._sauvegarder_index()
                return {
                    "status": "success",
                    "nb_embeddings": 0,
                    "message": "Index vide créé"
                }
            
            # Extraire les embeddings et IDs
            embeddings = []
            ids = []
            
            for ressource in ressources:
                embedding = ressource.get("embedding")
                if embedding and len(embedding) == self.embedding_dimension:
                    embeddings.append(embedding)
                    ids.append(str(ressource["_id"]))
            
            if not embeddings:
                logger.warning("⚠️ Aucun embedding valide trouvé")
                self.index = self._creer_index_faiss()
                self.resource_ids = []
                self._sauvegarder_index()
                return {
                    "status": "success",
                    "nb_embeddings": 0,
                    "message": "Aucun embedding valide"
                }
            
            # Créer l'index FAISS
            self.index = self._creer_index_faiss()
            
            # Convertir en numpy array
            embeddings_array = np.array(embeddings, dtype='float32')
            
            # Normaliser les embeddings pour la similarité cosine
            faiss.normalize_L2(embeddings_array)
            
            # Ajouter les embeddings à l'index
            self.index.add(embeddings_array)
            self.resource_ids = ids
            
            # Sauvegarder l'index sur disque
            self._sauvegarder_index()
            
            logger.info(f"✅ Index FAISS reconstruit avec {len(embeddings)} embeddings")
            
            return {
                "status": "success",
                "nb_embeddings": len(embeddings),
                "message": f"Index reconstruit avec succès"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur reconstruction index: {e}")
            # Créer un index vide en cas d'erreur
            self.index = self._creer_index_faiss()
            self.resource_ids = []
            return {
                "status": "error",
                "nb_embeddings": 0,
                "message": str(e)
            }
    
    async def ajouter_ressources_a_index(self, resource_ids: List[str]) -> Dict:
        """
        Ajoute de nouvelles ressources à l'index FAISS existant
        Appelé après un crawl pour mettre à jour l'index
        
        Args:
            resource_ids: Liste des IDs MongoDB des nouvelles ressources
            
        Returns:
            Dictionnaire avec les statistiques d'ajout
        """
        if not resource_ids:
            return {
                "status": "success",
                "nb_ajoutes": 0,
                "message": "Aucune ressource à ajouter"
            }
        
        logger.info(f"➕ Ajout de {len(resource_ids)} nouvelles ressources à l'index...")
        
        try:
            # Se connecter à MongoDB
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            collection = db[self.mongodb_collection]
            
            # Récupérer les embeddings des nouvelles ressources
            from bson import ObjectId
            object_ids = [ObjectId(rid) for rid in resource_ids]
            
            ressources = list(collection.find(
                {
                    "_id": {"$in": object_ids},
                    "embedding": {"$exists": True, "$ne": None}
                },
                {"_id": 1, "embedding": 1}
            ))
            
            client.close()
            
            if not ressources:
                return {
                    "status": "success",
                    "nb_ajoutes": 0,
                    "message": "Aucun embedding à ajouter"
                }
            
            # Extraire les embeddings
            embeddings = []
            ids = []
            
            for ressource in ressources:
                embedding = ressource.get("embedding")
                if embedding and len(embedding) == self.embedding_dimension:
                    embeddings.append(embedding)
                    ids.append(str(ressource["_id"]))
            
            if not embeddings:
                return {
                    "status": "success",
                    "nb_ajoutes": 0,
                    "message": "Aucun embedding valide"
                }
            
            # Créer l'index s'il n'existe pas
            if self.index is None:
                self.index = self._creer_index_faiss()
                self.resource_ids = []
            
            # Convertir en numpy array
            embeddings_array = np.array(embeddings, dtype='float32')
            
            # Normaliser les embeddings
            faiss.normalize_L2(embeddings_array)
            
            # Ajouter les embeddings à l'index
            self.index.add(embeddings_array)
            self.resource_ids.extend(ids)
            
            # Sauvegarder l'index mis à jour
            self._sauvegarder_index()
            
            logger.info(f"✅ {len(embeddings)} ressources ajoutées à l'index (total: {self.index.ntotal})")
            
            return {
                "status": "success",
                "nb_ajoutes": len(embeddings),
                "total_index": self.index.ntotal,
                "message": "Ressources ajoutées avec succès"
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur ajout à l'index: {e}")
            return {
                "status": "error",
                "nb_ajoutes": 0,
                "message": str(e)
            }
    
    async def recherche_semantique(
        self, 
        question: str, 
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Effectue une recherche sémantique dans l'index FAISS
        
        Args:
            question: Question de l'utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de tuples (resource_id, score_similarite)
        """
        if not question or not question.strip():
            return []
        
        if self.index is None or self.index.ntotal == 0:
            logger.warning("⚠️ Index FAISS vide, aucune recherche possible")
            return []
        
        try:
            # Générer l'embedding de la question
            question_embedding = self.generer_embedding(question)
            
            if question_embedding is None:
                return []
            
            # Préparer pour la recherche FAISS
            query_vector = question_embedding.reshape(1, -1)
            
            # Normaliser pour la similarité cosine
            faiss.normalize_L2(query_vector)
            
            # Recherche des k plus proches voisins
            k = min(top_k, self.index.ntotal)
            distances, indices = self.index.search(query_vector, k)
            
            # Construire les résultats
            resultats = []
            for idx, score in zip(indices[0], distances[0]):
                if idx < len(self.resource_ids):
                    resource_id = self.resource_ids[idx]
                    resultats.append((resource_id, float(score)))
            
            logger.info(f"🔍 Recherche sémantique: {len(resultats)} résultats trouvés")
            return resultats
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche sémantique: {e}")
            return []
    
    async def recherche_et_recuperer_ressources(
        self,
        question: str,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Effectue une recherche sémantique et récupère les ressources complètes
        
        Args:
            question: Question de l'utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de dictionnaires avec les ressources et leurs scores
        """
        # Recherche sémantique
        resultats_recherche = await self.recherche_semantique(question, top_k)
        
        if not resultats_recherche:
            return []
        
        try:
            # Récupérer les ressources depuis MongoDB
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            collection = db[self.mongodb_collection]
            
            from bson import ObjectId
            resource_ids = [ObjectId(rid) for rid, _ in resultats_recherche]
            
            ressources = list(collection.find({"_id": {"$in": resource_ids}}))
            
            client.close()
            
            # Créer un dictionnaire pour un accès rapide
            ressources_dict = {str(r["_id"]): r for r in ressources}
            
            # Construire les résultats avec scores
            resultats_finaux = []
            for resource_id, score in resultats_recherche:
                if resource_id in ressources_dict:
                    ressource = ressources_dict[resource_id]
                    ressource["_id"] = str(ressource["_id"])
                    ressource["score_similarite"] = score
                    resultats_finaux.append(ressource)
            
            logger.info(f"✅ {len(resultats_finaux)} ressources complètes récupérées")
            return resultats_finaux
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération ressources: {e}")
            return []
    
    def _sauvegarder_index(self):
        """Sauvegarde l'index FAISS et les IDs sur disque"""
        try:
            if self.index is not None:
                # Sauvegarder l'index FAISS
                faiss.write_index(self.index, f"{self.index_path}.index")
                
                # Sauvegarder les IDs des ressources
                with open(f"{self.index_path}.ids", 'wb') as f:
                    pickle.dump(self.resource_ids, f)
                
                logger.info(f"💾 Index FAISS sauvegardé ({self.index.ntotal} vecteurs)")
                
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde index: {e}")
    
    def charger_index(self) -> bool:
        """
        Charge l'index FAISS depuis le disque
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        try:
            index_file = f"{self.index_path}.index"
            ids_file = f"{self.index_path}.ids"
            
            if not os.path.exists(index_file) or not os.path.exists(ids_file):
                logger.info("ℹ️ Aucun index sauvegardé trouvé")
                return False
            
            # Charger l'index FAISS
            self.index = faiss.read_index(index_file)
            
            # Charger les IDs
            with open(ids_file, 'rb') as f:
                self.resource_ids = pickle.load(f)
            
            logger.info(f"✅ Index FAISS chargé ({self.index.ntotal} vecteurs)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement index: {e}")
            return False
    
    def obtenir_statistiques_index(self) -> Dict:
        """
        Retourne les statistiques de l'index FAISS
        
        Returns:
            Dictionnaire avec les statistiques
        """
        if self.index is None:
            return {
                "index_existe": False,
                "nb_vecteurs": 0,
                "dimension": self.embedding_dimension
            }
        
        return {
            "index_existe": True,
            "nb_vecteurs": self.index.ntotal,
            "dimension": self.embedding_dimension,
            "type_index": "IndexFlatIP (Inner Product)",
            "nb_resource_ids": len(self.resource_ids)
        }


# Instance singleton
_nlp_service_instance = None

def get_nlp_service(mongodb_url: str, mongodb_db: str, index_path: str = "data/faiss_index") -> NLPService:
    """
    Obtenir l'instance du service NLP (singleton)
    
    Args:
        mongodb_url: URL de connexion MongoDB
        mongodb_db: Nom de la base de données
        index_path: Chemin pour l'index FAISS
        
    Returns:
        Instance du service NLP
    """
    global _nlp_service_instance
    if _nlp_service_instance is None:
        _nlp_service_instance = NLPService(mongodb_url, mongodb_db, index_path)
    return _nlp_service_instance
