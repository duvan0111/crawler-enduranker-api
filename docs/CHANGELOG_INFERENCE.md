# 🎯 Résumé des modifications - Système de Tracking des Inférences

## Vue d'ensemble
Mise en place d'un système complet de tracking des inférences (recommandations) dans MongoDB pour tracer toutes les interactions entre les utilisateurs et les résultats du système de re-ranking.

---

## 📝 Fichiers modifiés

### 1. **Models** (`src/models/reranking_model.py`)
✅ Ajout du modèle `InferenceModel`
- Représente une recommandation du système
- Contient : user_query_id, resource_id, scores (FAISS, re-ranking, final), rank, feedback, dates, session_id

✅ Modification du modèle `RerankingRequestModel`
- Ajout du champ optionnel `session_id`

### 2. **Services** (`src/services/reranking_service.py`)
✅ Ajout de la collection `inference` dans `__init__`

✅ Nouvelle méthode `sauvegarder_inference()`
- Sauvegarde chaque recommandation dans MongoDB
- Paramètres : user_query_id, resource_id, faiss_score, reranking_score, final_score, rank, session_id
- Retourne : ID de l'inférence créée

✅ Modification de la méthode `sauvegarder_feedback()`
- Met à jour automatiquement le champ `feedback` dans la collection `inference`
- Utilise `update_one()` pour mettre à jour l'inférence correspondante

✅ Nouvelle méthode `recuperer_inferences(user_query_id)`
- Récupère toutes les inférences d'une requête utilisateur
- Trie par rang croissant
- Retourne : Liste des inférences avec tous leurs détails

### 3. **Controllers** (`src/controllers/reranking_controller.py`)
✅ Modification de `recherche_avec_reranking()`
- **Étape 0** : Sauvegarde la requête utilisateur via `user_query_service`
- Récupère l'ID de la requête (`user_query_id`)
- **Étape 3 modifiée** : Sauvegarde chaque inférence après le formatage des résultats
- Appelle `sauvegarder_inference()` pour chaque résultat retourné

✅ Nouvelle méthode `recuperer_inferences(user_query_id)`
- Récupère les inférences d'une requête
- Retourne un dictionnaire avec statut, nombre d'inférences et liste des inférences

### 4. **Routes** (`src/routes/reranking_routes.py`)
✅ Nouveau endpoint `GET /api/reranking/inferences/{user_query_id}`
- Récupère toutes les inférences pour une requête donnée
- Utile pour l'analyse et le debugging

### 5. **User Query Service** (`src/services/user_query_service.py`)
✅ Ajout de l'alias `get_user_query_service`
- Permet d'utiliser la fonction avec un nom cohérent
- `get_user_query_service = get_user_query_service_simple`

---

## 🗄️ Nouvelle Collection MongoDB

### Collection `inference`
Stocke toutes les recommandations faites par le système

**Structure :**
```javascript
{
  _id: ObjectId,
  user_query_id: String,        // Référence à users_queries
  resource_id: String,           // Référence à ressources_educatives
  faiss_score: Number,           // Score FAISS (0-1)
  reranking_score: Number,       // Score cross-encoder (peut être null)
  final_score: Number,           // Score final combiné
  rank: Number,                  // Position (1 = meilleur)
  feedback: String,              // "like", "dislike", "click", "view" ou null
  date_inference: Date,          // Date de la recommandation
  date_feedback: Date,           // Date du feedback (si donné)
  session_id: String,            // ID de session (optionnel)
  metadata: Object               // Métadonnées supplémentaires
}
```

**Index recommandés :**
1. `user_query_id` + `rank`
2. `resource_id`
3. `feedback`
4. `session_id`
5. `date_inference`
6. `feedback` + `date_inference`
7. `user_query_id` + `resource_id`

---

## 📜 Scripts ajoutés

### 1. `scripts/create_inference_indexes.py`
- Crée automatiquement tous les index recommandés
- Affiche des statistiques sur la collection
- Usage : `python scripts/create_inference_indexes.py`

### 2. `scripts/analyze_inferences.py`
- Génère des statistiques détaillées sur les inférences
- Analyse : scores, rangs, feedbacks, impact du re-ranking, top ressources
- Usage : `python scripts/analyze_inferences.py`

---

## 📚 Documentation ajoutée

### 1. `docs/INFERENCE_TRACKING.md`
Documentation complète du système :
- Structure de la collection
- Flux de données (diagrammes)
- Endpoints API détaillés
- Cas d'usage et requêtes MongoDB
- Métriques disponibles
- Relations entre collections

### 2. `docs/INFERENCE_QUICKSTART.md`
Guide de démarrage rapide :
- Utilisation des nouveaux endpoints
- Configuration MongoDB
- Scripts d'analyse
- Requêtes utiles
- Workflow complet
- Checklist de mise en production

---

## 🔄 Flux de données complet

```
1. Utilisateur → POST /recherche-avec-reranking
                  ↓
2. UserQueryService → Sauvegarde requête → user_query_id
                  ↓
3. NLPService → Recherche FAISS
                  ↓
4. RerankingService → Re-ranking
                  ↓
5. Pour chaque résultat:
   RerankingService → sauvegarder_inference()
                  ↓
   MongoDB → INSERT dans collection inference
                  ↓
6. Retour résultats à l'utilisateur
                  ↓
7. Utilisateur → POST /feedback
                  ↓
8. RerankingService → sauvegarder_feedback()
                  ↓
9. MongoDB → INSERT dans user_feedbacks
            → UPDATE inference (set feedback)
```

---

## 📊 Métriques disponibles

Grâce à la collection `inference`, vous pouvez maintenant calculer :

1. **CTR (Click-Through Rate)** par position
2. **Taux de satisfaction** (likes / (likes + dislikes))
3. **Position moyenne du premier clic**
4. **Efficacité du re-ranking** (amélioration des scores)
5. **Couverture des ressources** (nombre de ressources uniques)
6. **Diversité des recommandations**
7. **Comportement utilisateur** par session
8. **Performance temporelle** (évolution dans le temps)

---

## 🚀 Utilisation

### Exemple complet

```python
import requests

# 1. Recherche avec tracking
response = requests.post("http://localhost:8000/api/reranking/recherche-avec-reranking", 
    json={
        "question": "machine learning",
        "top_k_final": 10,
        "session_id": "session_123"
    }
)
results = response.json()

# 2. Feedback utilisateur
requests.post("http://localhost:8000/api/reranking/feedback",
    json={
        "user_query_id": "67...",
        "resource_id": "65...",
        "query_text": "machine learning",
        "resource_title": "ML Introduction",
        "feedback_type": "like"
    }
)

# 3. Récupérer les inférences
inferences = requests.get("http://localhost:8000/api/reranking/inferences/67...")
print(inferences.json())
```

---

## ✅ Tests à effectuer

1. **Fonctionnels**
   - [ ] Recherche avec `session_id` → inférences créées
   - [ ] Recherche sans `session_id` → fonctionne aussi
   - [ ] Feedback → mise à jour de l'inférence
   - [ ] GET inférences → récupération correcte

2. **Performance**
   - [ ] Créer les index MongoDB
   - [ ] Tester avec 1000+ inférences
   - [ ] Vérifier les temps de réponse

3. **Intégrité**
   - [ ] user_query_id valide dans inference
   - [ ] resource_id valide dans inference
   - [ ] Pas de doublons (même query + resource)

---

## 🎯 Bénéfices

✅ **Traçabilité complète** : Toutes les recommandations enregistrées  
✅ **Amélioration continue** : Données pour fine-tuning  
✅ **Analytics** : Comprendre le comportement utilisateur  
✅ **Debugging** : Identifier les problèmes facilement  
✅ **A/B Testing** : Comparer stratégies de ranking  
✅ **Métriques business** : CTR, satisfaction, conversion  

---

## 📋 TODO / Améliorations futures

- [ ] Dashboard de visualisation des inférences
- [ ] Alertes automatiques (baisse de CTR, satisfaction)
- [ ] Export automatique pour ML (training data)
- [ ] Système de recommandation basé sur les inférences
- [ ] Nettoyage automatique des vieilles inférences
- [ ] Intégration avec outils d'analytics (Google Analytics, Mixpanel)

---

**Date de mise à jour :** 8 décembre 2024  
**Version :** 1.0.0  
**Status :** ✅ Implémentation complète
