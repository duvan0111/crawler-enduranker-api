from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Gestionnaire de connexion à MongoDB"""
    client: AsyncIOMotorClient = None
    database = None

    @classmethod
    async def connect_db(cls):
        """Établir la connexion à MongoDB"""
        try:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            db_name = os.getenv("MONGODB_DB_NAME", "eduranker_db")
            
            # Connexion à MongoDB local (sans server_api)
            cls.client = AsyncIOMotorClient(mongodb_url)
            cls.database = cls.client[db_name]
            
            # Tester la connexion
            await cls.client.admin.command('ping')
            print(f"✅ Connexion réussie à MongoDB - Base de données: {db_name}")
            
        except Exception as e:
            print(f"❌ Erreur de connexion à MongoDB: {e}")
            raise e

    @classmethod
    async def close_db(cls):
        """Fermer la connexion à MongoDB"""
        if cls.client:
            cls.client.close()
            print("🔌 Connexion MongoDB fermée")

    @classmethod
    def get_database(cls):
        """Obtenir l'instance de la base de données"""
        return cls.database

    @classmethod
    def get_collection(cls, collection_name: str):
        """Obtenir une collection spécifique"""
        if cls.database is None:
            raise Exception("La base de données n'est pas connectée")
        return cls.database[collection_name]

# Instance globale
db = Database()
