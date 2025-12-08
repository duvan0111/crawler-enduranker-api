from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import logging

from src.routes import crawler_routes, user_query_routes, nlp_routes, reranking_routes
from src.database import db
from src.services.nlp_service import get_nlp_service

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage : connexion à MongoDB
    await db.connect_db()
    
    # Initialiser le service NLP et reconstruire l'index FAISS
    try:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
        index_path = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
        
        logger.info("🚀 Initialisation du service NLP...")
        nlp_service = get_nlp_service(mongodb_url, mongodb_db, index_path)
        
        # Essayer de charger l'index existant
        if nlp_service.charger_index():
            logger.info("✅ Index FAISS chargé depuis le disque")
        else:
            # Reconstruire l'index depuis MongoDB
            logger.info("🔄 Reconstruction de l'index FAISS depuis MongoDB...")
            result = await nlp_service.reconstruire_index_depuis_bd()
            logger.info(f"📊 Résultat reconstruction: {result}")
        
        # Afficher les statistiques
        stats = nlp_service.obtenir_statistiques_index()
        logger.info(f"📈 Statistiques index FAISS: {stats}")
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation service NLP: {e}")
    
    yield
    
    # Arrêt : fermeture de la connexion MongoDB
    await db.close_db()
    logger.info("👋 Application arrêtée")

# Créer l'application FastAPI
app = FastAPI(
    title=os.getenv("APP_NAME", "EduRanker Crawler API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="API Backend pour le projet EduRanker",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter le dossier public pour les fichiers statiques
app.mount("/public", StaticFiles(directory="public"), name="public")

# Enregistrer les routes
app.include_router(crawler_routes.router)
app.include_router(user_query_routes.router)
app.include_router(nlp_routes.router)
app.include_router(reranking_routes.router)

@app.get("/")
async def root():
    """Route racine de l'API"""
    return {
        "message": "Bienvenue sur l'API EduRanker Crawler",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "docs": "/docs",
        "database": "MongoDB connectée" if db.database is not None else "MongoDB non connectée"
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    mongodb_status = "connected" if db.database is not None else "disconnected"
    return {
        "status": "healthy",
        "mongodb": mongodb_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True") == "True"
    )
