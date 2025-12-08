#!/usr/bin/env python3
"""
Script d'analyse des inférences pour évaluer les performances du système.
Génère des statistiques et visualisations sur les recommandations.
"""

import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_inferences():
    """Analyse les inférences et génère des statistiques"""
    
    # Configuration
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db = os.getenv("MONGODB_DB_NAME", "eduranker_db")
    
    print(f"🔌 Connexion à MongoDB: {mongodb_url}")
    print(f"📁 Base de données: {mongodb_db}\n")
    
    try:
        client = MongoClient(mongodb_url)
        db = client[mongodb_db]
        inference_col = db["inference"]
        
        # 1. Statistiques générales
        print("=" * 60)
        print("📊 STATISTIQUES GÉNÉRALES")
        print("=" * 60)
        
        total = inference_col.count_documents({})
        print(f"Total d'inférences: {total}")
        
        if total == 0:
            print("\n⚠️  Aucune inférence trouvée dans la base de données.")
            print("   Effectuez des recherches avec re-ranking pour générer des données.\n")
            client.close()
            return
        
        # Nombre de requêtes uniques
        unique_queries = len(inference_col.distinct("user_query_id"))
        print(f"Requêtes utilisateur uniques: {unique_queries}")
        
        # Nombre de ressources uniques recommandées
        unique_resources = len(inference_col.distinct("resource_id"))
        print(f"Ressources uniques recommandées: {unique_resources}")
        
        # Moyenne de recommandations par requête
        avg_per_query = total / unique_queries if unique_queries > 0 else 0
        print(f"Moyenne de recommandations par requête: {avg_per_query:.1f}")
        
        # 2. Analyse des scores
        print("\n" + "=" * 60)
        print("📈 ANALYSE DES SCORES")
        print("=" * 60)
        
        pipeline_scores = [
            {
                "$group": {
                    "_id": None,
                    "avg_faiss": {"$avg": "$faiss_score"},
                    "avg_reranking": {"$avg": "$reranking_score"},
                    "avg_final": {"$avg": "$final_score"},
                    "min_final": {"$min": "$final_score"},
                    "max_final": {"$max": "$final_score"}
                }
            }
        ]
        
        scores_result = list(inference_col.aggregate(pipeline_scores))
        if scores_result:
            stats = scores_result[0]
            print(f"Score FAISS moyen: {stats['avg_faiss']:.4f}")
            print(f"Score Re-ranking moyen: {stats.get('avg_reranking', 'N/A')}")
            print(f"Score final moyen: {stats['avg_final']:.4f}")
            print(f"Score final min: {stats['min_final']:.4f}")
            print(f"Score final max: {stats['max_final']:.4f}")
        
        # 3. Distribution par rang
        print("\n" + "=" * 60)
        print("🏆 DISTRIBUTION PAR RANG")
        print("=" * 60)
        
        pipeline_ranks = [
            {"$group": {"_id": "$rank", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
            {"$limit": 10}
        ]
        
        rank_distribution = list(inference_col.aggregate(pipeline_ranks))
        for item in rank_distribution:
            rank = item['_id']
            count = item['count']
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 2)
            print(f"Rang {rank:2d}: {bar} {count:5d} ({percentage:5.1f}%)")
        
        # 4. Analyse des feedbacks
        print("\n" + "=" * 60)
        print("💬 ANALYSE DES FEEDBACKS")
        print("=" * 60)
        
        with_feedback = inference_col.count_documents({"feedback": {"$ne": None}})
        feedback_rate = (with_feedback / total) * 100
        print(f"Inférences avec feedback: {with_feedback} / {total} ({feedback_rate:.1f}%)")
        
        if with_feedback > 0:
            print("\nRépartition des feedbacks:")
            pipeline_feedback = [
                {"$match": {"feedback": {"$ne": None}}},
                {"$group": {"_id": "$feedback", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            feedback_dist = list(inference_col.aggregate(pipeline_feedback))
            for item in feedback_dist:
                fb_type = item['_id']
                count = item['count']
                percentage = (count / with_feedback) * 100
                emoji = {"like": "👍", "dislike": "👎", "click": "🖱️", "view": "👁️"}.get(fb_type, "❓")
                print(f"  {emoji} {fb_type}: {count} ({percentage:.1f}%)")
            
            # Taux de satisfaction (likes / (likes + dislikes))
            likes = inference_col.count_documents({"feedback": "like"})
            dislikes = inference_col.count_documents({"feedback": "dislike"})
            if likes + dislikes > 0:
                satisfaction = (likes / (likes + dislikes)) * 100
                print(f"\n😊 Taux de satisfaction: {satisfaction:.1f}%")
        
        # 5. Position moyenne des feedbacks
        print("\n" + "=" * 60)
        print("📍 POSITION MOYENNE DES FEEDBACKS")
        print("=" * 60)
        
        pipeline_feedback_rank = [
            {"$match": {"feedback": {"$ne": None}}},
            {"$group": {
                "_id": "$feedback",
                "avg_rank": {"$avg": "$rank"},
                "min_rank": {"$min": "$rank"},
                "max_rank": {"$max": "$rank"}
            }}
        ]
        
        feedback_ranks = list(inference_col.aggregate(pipeline_feedback_rank))
        for item in feedback_ranks:
            fb_type = item['_id']
            avg_rank = item['avg_rank']
            min_rank = item['min_rank']
            max_rank = item['max_rank']
            emoji = {"like": "👍", "dislike": "👎", "click": "🖱️", "view": "👁️"}.get(fb_type, "❓")
            print(f"{emoji} {fb_type}: rang moyen {avg_rank:.1f} (min: {min_rank}, max: {max_rank})")
        
        # 6. Impact du re-ranking
        print("\n" + "=" * 60)
        print("🔄 IMPACT DU RE-RANKING")
        print("=" * 60)
        
        with_reranking = inference_col.count_documents({"reranking_score": {"$ne": None}})
        print(f"Inférences avec re-ranking: {with_reranking} / {total}")
        
        if with_reranking > 0:
            pipeline_improvement = [
                {"$match": {"reranking_score": {"$ne": None}}},
                {"$project": {
                    "improvement": {"$subtract": ["$final_score", "$faiss_score"]}
                }},
                {"$group": {
                    "_id": None,
                    "avg_improvement": {"$avg": "$improvement"},
                    "positive_count": {
                        "$sum": {"$cond": [{"$gt": ["$improvement", 0]}, 1, 0]}
                    },
                    "total": {"$sum": 1}
                }}
            ]
            
            improvement_result = list(inference_col.aggregate(pipeline_improvement))
            if improvement_result:
                stats = improvement_result[0]
                avg_imp = stats['avg_improvement']
                pos_count = stats['positive_count']
                total_rerank = stats['total']
                pos_rate = (pos_count / total_rerank) * 100
                
                print(f"Amélioration moyenne du score: {avg_imp:+.4f}")
                print(f"Améliorations positives: {pos_count} / {total_rerank} ({pos_rate:.1f}%)")
        
        # 7. Top ressources recommandées
        print("\n" + "=" * 60)
        print("🌟 TOP 10 RESSOURCES RECOMMANDÉES")
        print("=" * 60)
        
        pipeline_top = [
            {"$group": {
                "_id": "$resource_id",
                "count": {"$sum": 1},
                "avg_rank": {"$avg": "$rank"},
                "avg_score": {"$avg": "$final_score"},
                "feedbacks": {"$push": "$feedback"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_resources = list(inference_col.aggregate(pipeline_top))
        for i, item in enumerate(top_resources, 1):
            resource_id = item['_id']
            count = item['count']
            avg_rank = item['avg_rank']
            avg_score = item['avg_score']
            feedbacks = [f for f in item['feedbacks'] if f is not None]
            fb_count = len(feedbacks)
            
            print(f"{i:2d}. Ressource {resource_id}")
            print(f"    Recommandée {count} fois (rang moyen: {avg_rank:.1f}, score: {avg_score:.3f})")
            if fb_count > 0:
                print(f"    Feedbacks: {fb_count}")
        
        client.close()
        print("\n" + "=" * 60)
        print("✅ Analyse terminée!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}\n")

if __name__ == "__main__":
    analyze_inferences()
