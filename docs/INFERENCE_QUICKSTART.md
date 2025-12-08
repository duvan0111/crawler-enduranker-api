# 🎯 Système de Tracking des Inférences - Guide de démarrage rapide

## Vue d'ensemble

Le système de tracking des inférences a été mis en place pour tracer toutes les recommandations faites par l'API. Chaque recherche génère des inférences qui sont stockées dans MongoDB avec leurs scores et peuvent être enrichies avec des feedbacks utilisateurs.

## 🆕 Nouveautés

### Modèles ajoutés

**`InferenceModel`** : Représente une recommandation du système
```python
{
    "user_query_id": str,       # ID de la requête
    "resource_id": str,          # ID de la ressource recommandée
    "faiss_score": float,        # Score FAISS (0-1)
    "reranking_score": float,    # Score cross-encoder (optionnel)
    "final_score": float,        # Score final combiné
    "rank": int,                 # Position (1 = meilleur)
    "feedback": str,             # "like", "dislike", "click", "view" ou null
    "date_inference": datetime,  # Date de la recommandation
    "session_id": str            # ID de session (optionnel)
}
```

### Endpoints modifiés

**POST `/api/reranking/recherche-avec-reranking`**
- Accepte maintenant un `session_id` optionnel
- Sauvegarde automatiquement les inférences dans MongoDB
- Retourne l'ID de la requête utilisateur dans les logs

**POST `/api/reranking/feedback`**
- Met à jour automatiquement le champ `feedback` dans la collection `inference`

### Nouveaux endpoints

**GET `/api/reranking/inferences/{user_query_id}`**
- Récupère toutes les inférences pour une requête donnée
- Utile pour analyser les recommandations faites

```bash
curl http://localhost:8000/api/reranking/inferences/507f1f77bcf86cd799439011
```

## 🚀 Utilisation

### 1. Effectuer une recherche avec tracking

```python
import requests

response = requests.post("http://localhost:8000/api/reranking/recherche-avec-reranking", json={
    "question": "machine learning pour débutants",
    "top_k_faiss": 50,
    "top_k_final": 10,
    "use_reranker": True,
    "session_id": "user_session_123"  # Nouveau paramètre optionnel
})

results = response.json()
# Les inférences sont automatiquement sauvegardées en arrière-plan
```

### 2. Soumettre un feedback

```python
# L'utilisateur clique sur une ressource
requests.post("http://localhost:8000/api/reranking/feedback", json={
    "user_query_id": "507f1f77bcf86cd799439011",
    "resource_id": "507f1f77bcf86cd799439012",
    "query_text": "machine learning pour débutants",
    "resource_title": "Introduction au ML",
    "feedback_type": "click",
    "session_id": "user_session_123"
})
# Met à jour automatiquement l'inférence correspondante
```

### 3. Récupérer les inférences d'une requête

```python
user_query_id = "507f1f77bcf86cd799439011"
response = requests.get(f"http://localhost:8000/api/reranking/inferences/{user_query_id}")

data = response.json()
print(f"Nombre d'inférences: {data['nb_inferences']}")
for inf in data['inferences']:
    print(f"Rang {inf['rank']}: {inf['resource_id']} - Score: {inf['final_score']:.3f}")
    if inf['feedback']:
        print(f"  Feedback: {inf['feedback']}")
```

## 🔧 Configuration MongoDB

### Créer les index optimisés

Pour de meilleures performances, créez les index recommandés :

```bash
python scripts/create_inference_indexes.py
```

Cela créera automatiquement :
- Index sur `user_query_id` + `rank`
- Index sur `resource_id`
- Index sur `feedback`
- Index sur `session_id`
- Index sur `date_inference`
- Et d'autres index composites

### Vérifier les inférences dans MongoDB

```bash
# Connexion à MongoDB
mongosh mongodb://localhost:27017/eduranker_db

# Compter les inférences
db.inference.countDocuments()

# Voir quelques exemples
db.inference.find().limit(5).pretty()

# Inférences avec feedback
db.inference.find({ feedback: { $ne: null } }).limit(5)
```

## 📊 Analyse des données

### Script d'analyse automatique

```bash
python scripts/analyze_inferences.py
```

Ce script génère :
- Statistiques générales (total, requêtes uniques, ressources uniques)
- Analyse des scores (moyennes, min, max)
- Distribution par rang
- Analyse des feedbacks (taux de feedback, satisfaction)
- Position moyenne des feedbacks
- Impact du re-ranking
- Top 10 des ressources recommandées

### Requêtes MongoDB utiles

**Taux de clics par position :**
```javascript
db.inference.aggregate([
  {
    $group: {
      _id: "$rank",
      total: { $sum: 1 },
      clicks: { $sum: { $cond: [{ $in: ["$feedback", ["click", "like"]] }, 1, 0] } }
    }
  },
  {
    $project: {
      rank: "$_id",
      ctr: { $multiply: [{ $divide: ["$clicks", "$total"] }, 100] }
    }
  },
  { $sort: { rank: 1 } }
])
```

**Ressources les plus performantes :**
```javascript
db.inference.aggregate([
  { $match: { feedback: { $in: ["like", "click"] } } },
  {
    $group: {
      _id: "$resource_id",
      nb_interactions: { $sum: 1 },
      avg_rank: { $avg: "$rank" },
      avg_score: { $avg: "$final_score" }
    }
  },
  { $sort: { nb_interactions: -1 } },
  { $limit: 20 }
])
```

**Efficacité du re-ranking :**
```javascript
db.inference.aggregate([
  { $match: { reranking_score: { $ne: null } } },
  {
    $project: {
      amelioration: { $subtract: ["$final_score", "$faiss_score"] },
      feedback: 1
    }
  },
  {
    $group: {
      _id: "$feedback",
      avg_amelioration: { $avg: "$amelioration" }
    }
  }
])
```

## 📈 Métriques disponibles

Avec la collection `inference`, vous pouvez calculer :

1. **CTR (Click-Through Rate)** : Taux de clics par position
2. **Taux de satisfaction** : Ratio likes/(likes+dislikes)
3. **Position moyenne du premier clic**
4. **Efficacité du re-ranking** : Amélioration des scores
5. **Couverture** : Nombre de ressources uniques recommandées
6. **Diversité** : Distribution des ressources par requête
7. **Temps de réponse** : Via les timestamps
8. **Comportement utilisateur** : Analyse par session

## 🔄 Workflow complet

```
1. Utilisateur fait une recherche
   ↓
2. API sauvegarde la requête dans users_queries
   ↓
3. Recherche FAISS + Re-ranking
   ↓
4. Pour chaque résultat : sauvegarde dans inference
   ↓
5. Résultats retournés à l'utilisateur
   ↓
6. Utilisateur interagit (click, like, etc.)
   ↓
7. Feedback sauvegardé dans user_feedbacks
   ↓
8. Mise à jour du champ feedback dans inference
   ↓
9. Données utilisées pour le fine-tuning
```

## 🛠️ Maintenance

### Nettoyage des anciennes inférences

```javascript
// Supprimer les inférences sans feedback de plus de 30 jours
db.inference.deleteMany({
  feedback: null,
  date_inference: { $lt: new Date(Date.now() - 30*24*60*60*1000) }
})
```

### Backup des inférences

```bash
# Export
mongoexport --db=eduranker_db --collection=inference --out=inference_backup.json

# Import
mongoimport --db=eduranker_db --collection=inference --file=inference_backup.json
```

## 📚 Documentation complète

Pour plus de détails, consultez :
- **[INFERENCE_TRACKING.md](docs/INFERENCE_TRACKING.md)** : Documentation complète
- **[RERANKING_SERVICE.md](docs/RERANKING_SERVICE.md)** : Service de re-ranking

## ✅ Checklist de mise en production

- [ ] Créer les index MongoDB (`python scripts/create_inference_indexes.py`)
- [ ] Tester les endpoints avec différents `session_id`
- [ ] Configurer le monitoring des inférences
- [ ] Mettre en place un système de nettoyage automatique
- [ ] Définir les métriques à surveiller
- [ ] Former l'équipe à l'analyse des données
- [ ] Planifier les A/B tests basés sur les inférences

## 🎉 Avantages

✅ **Traçabilité complète** : Toutes les recommandations sont enregistrées  
✅ **Amélioration continue** : Données pour le fine-tuning  
✅ **Analytics avancés** : Comprendre le comportement utilisateur  
✅ **Debugging facilité** : Identifier les problèmes de recommandation  
✅ **A/B testing** : Comparer différentes stratégies  
✅ **ROI mesurable** : Évaluer l'impact du système  

---

**Questions ou problèmes ?** Consultez la documentation complète ou ouvrez une issue.
