"""
Routes API pour le workflow global de traitement des requêtes.
"""

from fastapi import APIRouter, status, HTTPException
from src.models.workflow_model import WorkflowRequestModel, WorkflowResponseModel
from src.controllers.workflow_controller import workflow_controller

# Créer le routeur
router = APIRouter(
    prefix="/api/workflow",
    tags=["Workflow Global"],
    responses={404: {"description": "Non trouvé"}},
)


@router.post("/process", response_model=WorkflowResponseModel, status_code=status.HTTP_200_OK)
async def traiter_requete_complete(request: WorkflowRequestModel):
    """
    Traite une requête utilisateur de bout en bout et retourne le top 10 des meilleures ressources.
    
    Ce workflow comprend:
    1. Sauvegarde de la question de l'utilisateur
    2. Crawling des sources spécifiées (Wikipedia, GitHub, Medium)
    3. Reconstruction de l'index FAISS avec les nouvelles données
    4. Recherche sémantique avec FAISS
    5. Re-ranking des résultats avec un cross-encoder
    6. Sauvegarde des inférences
    7. Retour du top 10 des meilleures ressources
    
    **Exemple de requête:**
    ```json
    {
        "question": "Comment apprendre le machine learning ?",
        "max_par_site": 15,
        "sources": ["wikipedia", "github", "medium"],
        "langues": ["fr", "en"],
        "top_k_faiss": 50,
        "top_k_final": 10
    }
    ```
    
    **Paramètres:**
    - **question**: Question de l'utilisateur (requis)
    - **max_par_site**: Nombre maximum de résultats par site (optionnel, défaut: 15)
    - **sources**: Sources à crawler (optionnel, défaut: ["wikipedia", "github", "medium"])
    - **langues**: Langues pour Wikipedia (optionnel, défaut: ["fr", "en"])
    - **top_k_faiss**: Nombre de résultats FAISS avant re-ranking (optionnel, défaut: 50)
    - **top_k_final**: Nombre de résultats finaux (optionnel, défaut: 10)
    
    **Retourne:**
    - **question**: Question de l'utilisateur
    - **id_requete**: ID de la requête sauvegardée dans MongoDB
    - **total_crawle**: Nombre total de ressources crawlées
    - **total_resultats_faiss**: Nombre de résultats de la recherche FAISS
    - **total_resultats_final**: Nombre de résultats finaux (top 10)
    - **duree_crawl_secondes**: Durée du crawling
    - **duree_recherche_secondes**: Durée de la recherche FAISS
    - **duree_reranking_secondes**: Durée du re-ranking
    - **duree_totale_secondes**: Durée totale du traitement
    - **resultats**: Liste des 10 meilleures ressources avec:
      - **titre**: Titre de la ressource
      - **url**: URL de la ressource
      - **auteur**: Auteur (si disponible)
      - **date**: Date de publication (si disponible)
      - **score_faiss**: Score de similarité FAISS
      - **score_reranking**: Score du cross-encoder
      - **score_final**: Score final combiné
      - **mots_cles**: Mots-clés de la ressource
      - **source**: Source (wikipedia, github, medium)
      - **id_inference**: ID de l'inférence sauvegardée
    - **sources_crawlees**: Sources qui ont été crawlées
    - **erreurs**: Liste des erreurs éventuelles (si présentes)
    
    **Codes de retour:**
    - **200**: Succès - Résultats retournés
    - **400**: Erreur de validation des paramètres
    - **500**: Erreur serveur
    """
    try:
        reponse = await workflow_controller.traiter_requete(request)
        return reponse
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de la requête: {str(e)}"
        )


# @router.get("/health", status_code=status.HTTP_200_OK)
# async def verifier_sante_workflow():
#     """
#     Vérifie que le service de workflow est opérationnel.
    
#     **Retourne:**
#     - **status**: État du service
#     - **message**: Message d'information
#     """
#     return {
#         "status": "healthy",
#         "message": "Le service de workflow est opérationnel"
#     }
