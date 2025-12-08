# EduRanker Crawler API

Backend FastAPI pour le projet EduRanker avec système de crawling, recherche vectorielle et reranking intelligent.

## 🎯 Fonctionnalités

- **API REST complète** avec FastAPI
- **Crawler de ressources éducatives** depuis Wikipedia, GitHub, Medium
- **Recherche vectorielle FAISS** avec embeddings de pointe
- **Reranking intelligent** avec cross-encoder (Sentence-BERT)
- **Système d'inférence** : tracking automatique de toutes les recommandations
- **Feedback simplifié** : 2 champs seulement (inference_id + feedback_type)
- **Fine-tuning** : amélioration continue du modèle avec les feedbacks
- **Base de données MongoDB** pour le stockage
- **Documentation interactive** avec Swagger UI
- **Architecture MVC** (Models, Views, Controllers)
- **Tests automatisés** et scripts d'analyse

## 📁 Structure du projet

```
crawler-enduranker-api/
├── public/                    # Fichiers statiques
├── src/
│   ├── crawler/              # Système de crawling Scrapy
│   │   ├── spiders/          # Spiders Wikipedia, GitHub, Medium
│   │   └── utils/            # Utilitaires de crawling
│   ├── controllers/          # Logique de contrôle
│   ├── models/               # Modèles Pydantic
│   ├── routes/               # Routes API
│   ├── services/             # Logique métier
│   └── database.py           # Configuration MongoDB
├── venv/                     # Environnement virtuel
├── main.py                   # Point d'entrée
├── scrapy.cfg               # Configuration Scrapy
├── requirements.txt         # Dépendances
└── .env                     # Variables d'environnement
```

## Installation

1. Créer et activer l'environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Puis éditer le fichier .env selon votre configuration
```

## Configuration de MongoDB

Assurez-vous que MongoDB est installé et en cours d'exécution localement :

```bash
# Vérifier si MongoDB est en cours d'exécution
sudo systemctl status mongod

# Démarrer MongoDB si nécessaire
sudo systemctl start mongod

# Activer MongoDB au démarrage
sudo systemctl enable mongod
```

Par défaut, l'application se connecte à `mongodb://localhost:27017` avec la base de données `eduranker_db`.
Vous pouvez modifier ces valeurs dans le fichier `.env` :

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=eduranker_db
```

## Lancement

```bash
python main.py
# ou
uvicorn main:app --reload
```

L'API sera accessible sur `http://localhost:8000`

La documentation interactive sera disponible sur :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## 🚀 Utilisation de l'API Crawler

### Collecter des ressources éducatives

La route principale vous permet d'envoyer une question et de recevoir une liste d'articles/ressources :

```bash
curl -X POST "http://localhost:8000/api/crawler/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "machine learning en éducation"
  }'
```

**Avec paramètres personnalisés :**

```bash
curl -X POST "http://localhost:8000/api/crawler/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "deep learning",
    "max_par_site": 10,
    "sources": ["wikipedia", "github"],
    "langues": ["fr", "en"]
  }'
```

### Rechercher dans les ressources existantes

```bash
curl -X POST "http://localhost:8000/api/crawler/search" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "machine learning",
    "limite": 20
  }'
```

### Scripts de test

Pour tester rapidement l'API :

```bash
# Test de l'API CRUD de base
./test_api.sh

# Test de l'API Crawler
./test_crawler_api.sh
```

## Test de la connexion MongoDB

Pour vérifier que MongoDB fonctionne correctement :

```bash
# Test de connexion MongoDB
mongosh

# Dans le shell MongoDB
show dbs
use eduranker_db
show collections
```

## 🆕 Système d'Inférence et Feedback

Le système de **tracking d'inférence** et de **feedback simplifié** est maintenant opérationnel ! 🎉

### Démarrage Rapide (3 étapes)

```bash
# 1. Créer les index MongoDB (une seule fois)
python scripts/create_inference_indexes.py

# 2. Démarrer l'API
python main.py

# 3. Tester le système (dans un autre terminal)
python scripts/test_inference_flow.py
```

### Fonctionnalités Clés

- ✅ **Tracking automatique** : Toutes les recommandations sont sauvegardées
- ✅ **Feedback simplifié** : Seulement 2 champs (`inference_id` + `feedback_type`)
- ✅ **Analyse de performance** : Scripts d'analyse des données
- ✅ **Fine-tuning** : Préparation pour amélioration du modèle

### Endpoints Disponibles

```bash
# Recherche avec reranking (sauvegarde automatique des inférences)
POST /api/reranking/search-with-reranking
{
  "query_text": "machine learning tutorial",
  "session_id": "user_123"  // Optionnel
}

# Soumission de feedback (ULTRA-SIMPLIFIÉ)
POST /api/reranking/feedback
{
  "inference_id": "67567xyz...",  // De la réponse de recherche
  "feedback_type": "like"          // "like" | "dislike" | "click" | "view"
}

# Récupération des inférences
GET /api/reranking/inferences/{query_id}
```

### Tests Disponibles

```bash
# Test complet (recherche + feedbacks multiples + vérification)
python scripts/test_inference_flow.py

# Test rapide (1 recherche + 1 feedback)
python scripts/test_inference_flow.py --quick

# Test bash (si jq installé)
./scripts/test_quick.sh

# Analyser les données collectées
python scripts/analyze_inferences.py
```

### Documentation Complète

| Document | Description |
|----------|-------------|
| **`QUICK_START.md`** | 🚀 Guide de démarrage en 5 minutes |
| **`docs/TESTING_INFERENCE_FEEDBACK.md`** | 🧪 Guide de test complet |
| **`docs/FEEDBACK_SIMPLIFIE.md`** | 🎨 Intégration frontend |
| **`docs/INFERENCE_TRACKING.md`** | 👨‍💻 Documentation technique |
| **`scripts/README.md`** | 🔧 Utilisation des scripts |
| **`IMPLEMENTATION_COMPLETE.md`** | 📊 Vue d'ensemble système |
| **`FILES_SUMMARY.txt`** | 📦 Résumé des fichiers |

### Exemple d'Intégration Frontend

```javascript
// 1. Recherche
const response = await fetch('/api/reranking/search-with-reranking', {
  method: 'POST',
  body: JSON.stringify({ query_text: userQuery, session_id: sessionId })
});
const { results } = await response.json();

// 2. Afficher les résultats et ajouter handlers
results.forEach(result => {
  // Stocker l'inference_id pour chaque résultat
  const inferenceId = result.inference_id;
  
  // Sur like/dislike
  likeButton.onclick = () => submitFeedback(inferenceId, 'like');
  
  // Sur clic de la ressource
  resourceLink.onclick = () => submitFeedback(inferenceId, 'click');
});

// 3. Fonction de soumission
async function submitFeedback(inferenceId, feedbackType) {
  await fetch('/api/reranking/feedback', {
    method: 'POST',
    body: JSON.stringify({ inference_id: inferenceId, feedback_type: feedbackType })
  });
}
```

### Base de Données MongoDB

**Collection `inference`** : Stocke toutes les recommandations
```javascript
{
  "_id": ObjectId("..."),
  "user_query_id": "...",     // ID de la requête
  "resource_id": "...",        // ID de la ressource recommandée
  "faiss_score": 0.85,         // Score FAISS
  "reranking_score": 0.92,     // Score cross-encoder
  "final_score": 0.88,         // Score final
  "rank": 1,                   // Position (1-N)
  "feedback": "like",          // Feedback utilisateur
  "date_inference": ISODate,   // Date de recommandation
  "date_feedback": ISODate,    // Date du feedback
  "session_id": "..."          // Session utilisateur
}
```

**5 index créés** pour optimiser les performances :
- `user_query_id` - Récupération rapide
- `resource_id` - Analyse par ressource
- `feedback` - Statistiques
- `session_id` - Suivi utilisateur
- `date_inference` - Tri chronologique

### Prochaines Étapes

1. **Collecter des données** : Laisser le système tourner et collecter des feedbacks
2. **Analyser** : `python scripts/analyze_inferences.py`
3. **Fine-tuner** : `POST /api/reranking/fine-tune?num_epochs=3`
4. **Optimiser** : Ajuster le modèle en fonction des résultats
