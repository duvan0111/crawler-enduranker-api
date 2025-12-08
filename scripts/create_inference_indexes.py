#!/usr/bin/env python3
"""
Script pour créer les index MongoDB pour la collection inference.
Optimise les performances des requêtes sur les inférences.
"""

import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING

def create_inference_indexes():
    """Crée les index optimisés pour la collection inference"""
    
    # Configuration
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
    
    print(f"🔌 Connexion à MongoDB: {mongodb_url}")
    print(f"📁 Base de données: {mongodb_db}")
    
    try:
        # Connexion
        client = MongoClient(mongodb_url)
        db = client[mongodb_db]
        inference_col = db["inference"]
        
        print("\n📊 Création des index pour la collection 'inference'...")
        
        # Index 1: Recherche par requête utilisateur et rang
        print("  ➡️  Index: user_query_id + rank")
        inference_col.create_index([
            ("user_query_id", ASCENDING),
            ("rank", ASCENDING)
        ], name="idx_user_query_rank")
        
        # Index 2: Recherche par ressource
        print("  ➡️  Index: resource_id")
        inference_col.create_index([
            ("resource_id", ASCENDING)
        ], name="idx_resource_id")
        
        # Index 3: Analyse des feedbacks
        print("  ➡️  Index: feedback")
        inference_col.create_index([
            ("feedback", ASCENDING)
        ], name="idx_feedback")
        
        # Index 4: Filtrage par session
        print("  ➡️  Index: session_id")
        inference_col.create_index([
            ("session_id", ASCENDING)
        ], name="idx_session_id")
        
        # Index 5: Requêtes temporelles
        print("  ➡️  Index: date_inference (desc)")
        inference_col.create_index([
            ("date_inference", DESCENDING)
        ], name="idx_date_inference")
        
        # Index 6: Composite pour analyse des feedbacks par date
        print("  ➡️  Index: feedback + date_inference")
        inference_col.create_index([
            ("feedback", ASCENDING),
            ("date_inference", DESCENDING)
        ], name="idx_feedback_date")
        
        # Index 7: Recherche optimisée user_query + resource (pour feedbacks)
        print("  ➡️  Index: user_query_id + resource_id")
        inference_col.create_index([
            ("user_query_id", ASCENDING),
            ("resource_id", ASCENDING)
        ], name="idx_user_query_resource", unique=False)
        
        print("\n✅ Tous les index ont été créés avec succès!")
        
        # Afficher les statistiques
        print("\n📈 Statistiques de la collection:")
        count = inference_col.count_documents({})
        print(f"  📊 Nombre total d'inférences: {count}")
        
        if count > 0:
            # Statistiques sur les feedbacks
            with_feedback = inference_col.count_documents({"feedback": {"$ne": None}})
            print(f"  💬 Inférences avec feedback: {with_feedback} ({with_feedback/count*100:.1f}%)")
            
            # Top 3 des rangs les plus fréquents
            pipeline = [
                {"$group": {"_id": "$rank", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 3}
            ]
            top_ranks = list(inference_col.aggregate(pipeline))
            if top_ranks:
                print(f"  🏆 Rangs les plus fréquents:")
                for item in top_ranks:
                    print(f"     - Rang {item['_id']}: {item['count']} fois")
        
        # Lister tous les index
        print("\n📑 Index créés:")
        indexes = inference_col.list_indexes()
        for idx in indexes:
            print(f"  • {idx['name']}: {idx.get('key', {})}")
        
        client.close()
        print("\n✨ Configuration terminée!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  Configuration des index MongoDB pour les inférences")
    print("=" * 60)
    create_inference_indexes()
