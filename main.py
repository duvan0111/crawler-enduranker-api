from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from src.routes import example_routes, crawler_routes
from src.database import db

# Charger les variables d'environnement
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage : connexion à MongoDB
    await db.connect_db()
    yield
    # Arrêt : fermeture de la connexion MongoDB
    await db.close_db()

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
app.include_router(example_routes.router)
app.include_router(crawler_routes.router)

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
