"""
Service pour le workflow global de traitement des requêtes utilisateur.
Orchestre le crawling, la recherche sémantique et le re-ranking.
"""

import logging
import time
from typing import List, Dict, Optional
from datetime import datetime

from src.services.crawler_service import get_simple_crawler_service
from src.services.user_query_service import get_user_query_service_simple
from src.services.nlp_service import get_nlp_service
from src.services.reranking_service import get_reranking_service
from src.models.workflow_model import (
    WorkflowRequestModel,
    WorkflowResponseModel,
    RessourceResultatModel
)

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service pour orchestrer le workflow complet de traitement"""
    
    def __init__(
        self,
        mongodb_url: str,
        mongodb_db: str,
        index_path: str = "data/faiss_index"
    ):
        """
        Initialise le service de workflow
        
        Args:
            mongodb_url: URL de connexion MongoDB
            mongodb_db: Nom de la base de données
            index_path: Chemin de l'index FAISS
        """
        self.mongodb_url = mongodb_url
        self.mongodb_db = mongodb_db
        self.index_path = index_path
        
        # Initialiser les services nécessaires
        logger.info("🔧 Initialisation des services du workflow...")
        
        self.crawler_service = get_simple_crawler_service(mongodb_url, mongodb_db)
        self.user_query_service = get_user_query_service_simple(mongodb_url, mongodb_db)
        self.nlp_service = get_nlp_service(mongodb_url, mongodb_db, index_path)
        self.reranking_service = get_reranking_service(mongodb_url, mongodb_db)
        
        logger.info("✅ Services du workflow initialisés")
    
    async def traiter_requete_complete(
        self,
        request: WorkflowRequestModel
    ) -> WorkflowResponseModel:
        """
        Traite une requête utilisateur de bout en bout
        
        Workflow:
        1. Sauvegarder la question de l'utilisateur
        2. Lancer le crawling sur les sources demandées
        3. Reconstruire l'index FAISS avec les nouvelles données
        4. Effectuer la recherche sémantique avec FAISS
        5. Re-ranker les résultats avec le cross-encoder
        6. Sauvegarder les inférences
        7. Retourner le top 10 des meilleures ressources
        
        Args:
            request: Paramètres de la requête
            
        Returns:
            Résultats du workflow complet
        """
        temps_debut_total = time.time()
        erreurs = []
        
        logger.info(f"🚀 Début du workflow pour la question: {request.question}")
        
        try:
            # ============================================================
            # ÉTAPE 1: Sauvegarder la question de l'utilisateur
            # ============================================================
            logger.info("📝 ÉTAPE 1/6: Sauvegarde de la question utilisateur...")
            temps_debut_etape = time.time()
            
            try:
                requete_sauvegardee = await self.user_query_service.sauvegarder_requete_async(
                    request.question
                )
                id_requete = requete_sauvegardee["id"]
                logger.info(f"✅ Question sauvegardée (ID: {id_requete})")
            except Exception as e:
                logger.error(f"❌ Erreur sauvegarde question: {e}")
                erreurs.append(f"Erreur sauvegarde question: {str(e)}")
                id_requete = "non_sauvegarde"
            
            # ============================================================
            # ÉTAPE 2: Lancer le crawling
            # ============================================================
            logger.info("🕷️  ÉTAPE 2/6: Lancement du crawling...")
            temps_debut_crawl = time.time()
            
            try:
                resultats_crawl = await self.crawler_service.rechercher_ressources_async(
                    requete=request.question,
                    max_par_site=request.max_par_site,
                    sources=request.sources,
                    langues=request.langues
                )
                
                duree_crawl = time.time() - temps_debut_crawl
                total_crawle = resultats_crawl.get("total_collecte", 0)
                sources_crawlees = resultats_crawl.get("sources_utilisees", [])
                
                logger.info(f"✅ Crawling terminé: {total_crawle} ressources en {duree_crawl:.2f}s")
                
                # Ajouter les erreurs du crawling
                if resultats_crawl.get("erreurs"):
                    erreurs.extend(resultats_crawl["erreurs"])
                
            except Exception as e:
                logger.error(f"❌ Erreur crawling: {e}")
                erreurs.append(f"Erreur crawling: {str(e)}")
                duree_crawl = 0
                total_crawle = 0
                sources_crawlees = []
            
            # ============================================================
            # ÉTAPE 3: Reconstruire l'index FAISS
            # ============================================================
            logger.info("🔄 ÉTAPE 3/6: Reconstruction de l'index FAISS...")
            temps_debut_index = time.time()
            
            try:
                resultat_index = await self.nlp_service.reconstruire_index_depuis_bd()
                logger.info(f"✅ Index FAISS reconstruit: {resultat_index.get('total_vecteurs', 0)} vecteurs")
            except Exception as e:
                logger.error(f"❌ Erreur reconstruction index: {e}")
                erreurs.append(f"Erreur reconstruction index: {str(e)}")
            
            # ============================================================
            # ÉTAPE 4: Recherche sémantique avec FAISS
            # ============================================================
            logger.info("🔍 ÉTAPE 4/6: Recherche sémantique avec FAISS...")
            temps_debut_recherche = time.time()
            
            try:
                resultats_faiss = await self.nlp_service.rechercher_ressources_similaires(
                    question=request.question,
                    top_k=request.top_k_faiss
                )
                
                duree_recherche = time.time() - temps_debut_recherche
                total_resultats_faiss = len(resultats_faiss)
                
                logger.info(f"✅ Recherche FAISS: {total_resultats_faiss} résultats en {duree_recherche:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Erreur recherche FAISS: {e}")
                erreurs.append(f"Erreur recherche FAISS: {str(e)}")
                resultats_faiss = []
                duree_recherche = 0
                total_resultats_faiss = 0
            
            # ============================================================
            # ÉTAPE 5: Re-ranking avec cross-encoder
            # ============================================================
            logger.info("🎯 ÉTAPE 5/6: Re-ranking avec cross-encoder...")
            temps_debut_reranking = time.time()
            
            try:
                resultats_rerankes = await self.reranking_service.reranker_resultats(
                    question=request.question,
                    resultats_faiss=resultats_faiss,
                    top_k=request.top_k_final
                )
                
                duree_reranking = time.time() - temps_debut_reranking
                logger.info(f"✅ Re-ranking terminé: {len(resultats_rerankes)} résultats en {duree_reranking:.2f}s")
                
            except Exception as e:
                logger.error(f"❌ Erreur re-ranking: {e}")
                erreurs.append(f"Erreur re-ranking: {str(e)}")
                resultats_rerankes = resultats_faiss[:request.top_k_final]
                duree_reranking = 0
            
            # ============================================================
            # ÉTAPE 6: Sauvegarder les inférences et formater les résultats
            # ============================================================
            logger.info("💾 ÉTAPE 6/6: Sauvegarde des inférences...")
            
            resultats_finaux = []
            
            for idx, resultat in enumerate(resultats_rerankes):
                try:
                    # Calculer le score final (moyenne pondérée)
                    score_faiss = resultat.get("score_faiss", 0.0)
                    score_reranking = resultat.get("score_reranking", 0.0)
                    score_final = (0.3 * score_faiss + 0.7 * score_reranking) if score_reranking else score_faiss
                    
                    # Sauvegarder l'inférence dans MongoDB
                    inference_result = await self.reranking_service.sauvegarder_inference(
                        user_query_id=id_requete,
                        resource_id=str(resultat.get("_id", resultat.get("id", ""))),
                        faiss_score=score_faiss,
                        reranking_score=score_reranking,
                        final_score=score_final,
                        rank=idx + 1
                    )
                    
                    id_inference = inference_result.get("inference_id", "unknown")
                    
                    # Formater le résultat
                    ressource_formatee = RessourceResultatModel(
                        titre=resultat.get("titre", "Sans titre"),
                        url=resultat.get("url", ""),
                        auteur=resultat.get("auteur"),
                        date=resultat.get("date"),
                        resume=resultat.get("resume"),
                        score_faiss=score_faiss,
                        score_reranking=score_reranking,
                        score_final=score_final,
                        mots_cles=resultat.get("mots_cles", []),
                        source=resultat.get("source", "inconnu"),
                        id_inference=id_inference
                    )
                    
                    resultats_finaux.append(ressource_formatee)
                    
                except Exception as e:
                    logger.error(f"❌ Erreur sauvegarde inférence pour résultat {idx}: {e}")
                    erreurs.append(f"Erreur sauvegarde inférence: {str(e)}")
            
            # ============================================================
            # Préparer la réponse finale
            # ============================================================
            duree_totale = time.time() - temps_debut_total
            
            logger.info(f"✅ Workflow terminé en {duree_totale:.2f}s")
            logger.info(f"📊 Résultats: {len(resultats_finaux)} ressources finales")
            
            reponse = WorkflowResponseModel(
                question=request.question,
                id_requete=id_requete,
                total_crawle=total_crawle,
                total_resultats_faiss=total_resultats_faiss,
                total_resultats_final=len(resultats_finaux),
                duree_crawl_secondes=round(duree_crawl, 2),
                duree_recherche_secondes=round(duree_recherche, 3),
                duree_reranking_secondes=round(duree_reranking, 2),
                duree_totale_secondes=round(duree_totale, 2),
                resultats=resultats_finaux,
                sources_crawlees=sources_crawlees,
                erreurs=erreurs if erreurs else None
            )
            
            return reponse
            
        except Exception as e:
            logger.error(f"❌ Erreur critique dans le workflow: {e}")
            raise


# Singleton pour le service de workflow
_workflow_service_instance = None


def get_workflow_service(
    mongodb_url: str,
    mongodb_db: str,
    index_path: str = "data/faiss_index"
) -> WorkflowService:
    """
    Retourne une instance singleton du service de workflow
    
    Args:
        mongodb_url: URL de connexion MongoDB
        mongodb_db: Nom de la base de données
        index_path: Chemin de l'index FAISS
        
    Returns:
        Instance du WorkflowService
    """
    global _workflow_service_instance
    
    if _workflow_service_instance is None:
        _workflow_service_instance = WorkflowService(
            mongodb_url=mongodb_url,
            mongodb_db=mongodb_db,
            index_path=index_path
        )
    
    return _workflow_service_instance
