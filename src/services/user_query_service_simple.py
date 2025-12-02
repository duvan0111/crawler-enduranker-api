"""
Version simplifiée du service de requêtes utilisateur sans les dépendances lourdes.
Cette version utilise un système d'embedding basique sans sentence-transformers.
"""

import logging
import pymongo
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from src.models.user_query_model import UserQueryModel, UserQueryResponseModel

logger = logging.getLogger(__name__)


class UserQueryServiceSimple:
    """Service simplifié pour gérer les requêtes utilisateur sans embeddings complexes"""
    
    def __init__(self, mongodb_url: str, mongodb_db: str):
        """Initialise le service des requêtes utilisateur"""
        self.mongodb_url = mongodb_url
        self.mongodb_db = mongodb_db
        self.mongodb_collection = "users_queries"
        
        # Vérifier la connexion MongoDB
        self._verifier_connexion_mongo()
        
    def _verifier_connexion_mongo(self):
        """Vérifie que la connexion MongoDB est disponible"""
        try:
            client = pymongo.MongoClient(self.mongodb_url, serverSelectionTimeoutMS=5000)
            client.server_info()
            client.close()
            logger.info("✅ Connexion MongoDB vérifiée pour UserQueryService")
        except Exception as e:
            error_msg = f"❌ Impossible de se connecter à MongoDB: {e}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    def _detecter_langue_simple(self, text: str) -> Optional[str]:
        """Détection de langue basique"""
        try:
            # Mots français communs
            mots_fr = ['le', 'la', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout', 'plus', 'par', 'grand', 'ce', 'voir', 'savoir', 'pouvoir', 'comment', 'apprendre', 'machine', 'données']
            # Mots anglais communs
            mots_en = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'water', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part', 'over', 'new', 'sound', 'take', 'only', 'little', 'work', 'know', 'place', 'year', 'live', 'me', 'back', 'give', 'most', 'very', 'after', 'thing', 'our', 'just', 'name', 'good', 'sentence', 'man', 'think', 'say', 'great', 'where', 'help', 'through', 'much', 'before', 'line', 'right', 'too', 'mean', 'old', 'any', 'same', 'tell', 'boy', 'follow', 'came', 'want', 'show', 'also', 'around', 'form', 'three', 'small', 'set', 'put', 'end', 'why', 'again', 'turn', 'here', 'off', 'went', 'old', 'number', 'great', 'tell', 'men', 'say', 'small', 'every', 'found', 'still', 'between', 'mane', 'should', 'home', 'big', 'give', 'air', 'line', 'set', 'own', 'under', 'read', 'last', 'never', 'us', 'left', 'end', 'along', 'while', 'might', 'next', 'sound', 'below', 'saw', 'something', 'thought', 'both', 'few', 'those', 'always', 'show', 'large', 'often', 'together', 'asked', 'house', 'don', 'world', 'going', 'want', 'school', 'important', 'until', 'form', 'food', 'keep', 'children', 'feet', 'land', 'side', 'without', 'boy', 'once', 'animal', 'life', 'enough', 'took', 'sometimes', 'four', 'head', 'above', 'kind', 'began', 'almost', 'live', 'page', 'got', 'earth', 'need', 'far', 'hand', 'high', 'year', 'mother', 'light', 'country', 'father', 'let', 'night', 'picture', 'being', 'study', 'second', 'soon', 'story', 'since', 'white', 'ever', 'paper', 'hard', 'near', 'sentence', 'better', 'best', 'across', 'during', 'today', 'however', 'sure', 'knew', 'it', 'try', 'told', 'young', 'sun', 'thing', 'whole', 'hear', 'example', 'heard', 'several', 'change', 'answer', 'room', 'sea', 'against', 'top', 'turned', 'learn', 'point', 'city', 'play', 'toward', 'five', 'himself', 'usually', 'money', 'seen', 'didn', 'car', 'morning', 'I', 'listed', 'am', 'an', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'were', 'will', 'with', 'learning', 'deep', 'machine', 'data']
            
            text_lower = text.lower()
            words = text_lower.split()
            
            fr_count = sum(1 for word in words if word in mots_fr)
            en_count = sum(1 for word in words if word in mots_en)
            
            if fr_count > en_count:
                return 'fr'
            elif en_count > 0:
                return 'en'
            else:
                return 'unknown'
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur détection langue: {e}")
            return 'unknown'
    
    def _generer_embedding_simple(self, question: str) -> Optional[List[float]]:
        """Génère un embedding simple basé sur un hash de la question"""
        try:
            # Utilise un hash MD5 pour créer un "embedding" basique
            hash_obj = hashlib.md5(question.lower().encode())
            hash_hex = hash_obj.hexdigest()
            
            # Convertit le hash en vecteur de 16 floats entre -1 et 1
            embedding = []
            for i in range(0, len(hash_hex), 2):
                hex_pair = hash_hex[i:i+2]
                int_val = int(hex_pair, 16)
                # Normalise entre -1 et 1
                float_val = (int_val - 127.5) / 127.5
                embedding.append(float_val)
            
            return embedding[:16]  # Limite à 16 dimensions
            
        except Exception as e:
            logger.error(f"❌ Erreur génération embedding: {e}")
            return None
    
    async def sauvegarder_requete(self, question: str) -> UserQueryResponseModel:
        """
        Sauvegarde une requête utilisateur avec son embedding dans MongoDB
        """
        try:
            # Détecter la langue
            langue_detectee = self._detecter_langue_simple(question)
            
            # Générer l'embedding simple
            embedding = self._generer_embedding_simple(question)
            
            # Créer le modèle de requête
            user_query = UserQueryModel(
                question=question,
                date_creation=datetime.now(),
                embedding=embedding,
                langue_detectee=langue_detectee
            )
            
            # Sauvegarder dans MongoDB
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            collection = db[self.mongodb_collection]
            
            # Vérifier si la question existe déjà récemment (même question dans les 24h)
            depuis_24h = datetime.now() - timedelta(hours=24)
            
            existing = collection.find_one({
                'question': question,
                'date_creation': {'$gte': depuis_24h}
            })
            
            if existing:
                # Retourner l'existante
                client.close()
                return UserQueryResponseModel(
                    id=str(existing['_id']),
                    question=existing['question'],
                    date_creation=existing['date_creation'],
                    embedding_genere=existing.get('embedding') is not None,
                    langue_detectee=existing.get('langue_detectee')
                )
            
            # Insérer la nouvelle requête
            result = collection.insert_one(user_query.dict())
            client.close()
            
            logger.info(f"💾 Requête sauvegardée: '{question}' (ID: {result.inserted_id})")
            
            return UserQueryResponseModel(
                id=str(result.inserted_id),
                question=question,
                date_creation=user_query.date_creation,
                embedding_genere=embedding is not None,
                langue_detectee=langue_detectee
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde requête: {e}")
            raise
    
    async def obtenir_requetes_recentes(self, limite: int = 50) -> List[Dict]:
        """Obtient les requêtes utilisateur récentes"""
        try:
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            collection = db[self.mongodb_collection]
            
            # Récupérer les requêtes récentes
            requetes = list(
                collection.find({}, {'embedding': 0})  # Exclure les embeddings (trop volumineux)
                .sort('date_creation', -1)
                .limit(limite)
            )
            
            client.close()
            
            # Convertir ObjectId en string
            for requete in requetes:
                requete['_id'] = str(requete['_id'])
            
            logger.info(f"📋 Récupération de {len(requetes)} requêtes récentes")
            return requetes
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération requêtes: {e}")
            return []
    
    async def obtenir_statistiques_requetes(self) -> Dict:
        """Obtient les statistiques sur les requêtes utilisateur"""
        try:
            client = pymongo.MongoClient(self.mongodb_url)
            db = client[self.mongodb_db]
            collection = db[self.mongodb_collection]
            
            # Total des requêtes
            total_requetes = collection.count_documents({})
            
            # Requêtes par langue
            pipeline_langues = [
                {"$group": {
                    "_id": "$langue_detectee",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}}
            ]
            stats_langues = list(collection.aggregate(pipeline_langues))
            
            # Requêtes par jour (7 derniers jours)
            depuis_7j = datetime.now() - timedelta(days=7)
            
            pipeline_par_jour = [
                {"$match": {"date_creation": {"$gte": depuis_7j}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date_creation"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]
            stats_par_jour = list(collection.aggregate(pipeline_par_jour))
            
            # Requêtes avec embedding
            requetes_avec_embedding = collection.count_documents({"embedding": {"$ne": None}})
            
            client.close()
            
            return {
                'total_requetes': total_requetes,
                'requetes_avec_embedding': requetes_avec_embedding,
                'taux_embedding': round((requetes_avec_embedding / total_requetes * 100), 2) if total_requetes > 0 else 0,
                'par_langue': {stat['_id']: stat['count'] for stat in stats_langues},
                'par_jour_7j': {stat['_id']: stat['count'] for stat in stats_par_jour},
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statistiques requêtes: {e}")
            return {}


# Instance singleton
_user_query_service_simple_instance = None

def get_user_query_service_simple(mongodb_url: str, mongodb_db: str) -> UserQueryServiceSimple:
    """Obtenir l'instance du service de requêtes utilisateur simplifié"""
    global _user_query_service_simple_instance
    if _user_query_service_simple_instance is None:
        _user_query_service_simple_instance = UserQueryServiceSimple(mongodb_url, mongodb_db)
    return _user_query_service_simple_instance
