# 🎓 EduRanker - API Backend Intelligente

> **Système de recommandation de ressources éducatives avec IA**
> 
> Backend FastAPI avancé combinant crawling intelligent, recherche sémantique FAISS, et re-ranking par deep learning pour fournir les meilleures ressources éducatives.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table des Matières

- [Vue d'Ensemble](#-vue-densemble)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Architecture](#-architecture)
- [Workflow Global](#-workflow-global)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [API Endpoints](#-api-endpoints)
- [Technologies](#-technologies)
- [Documentation](#-documentation)
- [Tests](#-tests)
- [Performances](#-performances)
- [Contributing](#-contributing)

---

## 🌟 Vue d'Ensemble

**EduRanker** est une API backend intelligente qui permet de découvrir, analyser et classer automatiquement les meilleures ressources éducatives sur le web. Le système utilise des techniques avancées de NLP et de Machine Learning pour comprendre les questions des utilisateurs et leur fournir les ressources les plus pertinentes.

### 🎯 Objectifs du Projet

- **Automatiser** la recherche de ressources éducatives de qualité
- **Classifier** intelligemment les ressources par pertinence
- **Apprendre** continuellement des interactions utilisateurs
- **Fournir** des recommandations personnalisées et précises

### 🚀 Cas d'Usage

- **Plateformes e-learning** : Recommandation de cours et tutoriels
- **Assistants éducatifs** : Réponses contextuelles avec ressources
- **Moteurs de recherche académiques** : Classement intelligent
- **Systèmes de gestion des connaissances** : Curation automatique

---

## ✨ Fonctionnalités Principales

### 🔥 Workflow Global (All-in-One)

Le **workflow global** est la fonctionnalité phare qui traite une requête de bout en bout :

```bash
Question → Crawling → Recherche Sémantique → Re-ranking → Top 10 Résultats
```

**Une seule requête API pour tout obtenir !**

```bash
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment apprendre le machine learning ?"}'
```

➡️ **[Guide Complet du Workflow](docs/WORKFLOW_GUIDE.md)**

### 🕷️ Crawler Multi-Sources Intelligent

- **Wikipedia** : Articles éducatifs multilingues (FR/EN)
- **GitHub** : Repositories, README, documentation
- **YouTube** : Vidéos éducatives via API officielle (gratuit, 10k requêtes/jour) 🆕
- **Medium** : Articles de blog et tutoriels
- **Génération automatique d'embeddings** (384 dimensions)
- **Extraction de métadonnées** : auteur, date, mots-clés, popularité

➡️ **[Guide YouTube Integration](docs/YOUTUBE_INTEGRATION.md)**

### 🔍 Recherche Sémantique FAISS

- **Index vectoriel FAISS** pour recherche ultra-rapide
- **Sentence-Transformers** (all-MiniLM-L6-v2)
- **Similarité cosine** pour matching sémantique
- **Scalable** : Gère des millions de ressources
- **Persistance** : Sauvegarde/chargement de l'index

### 🎯 Re-ranking avec Cross-Encoder

- **Modèle BERT** (ms-marco-MiniLM-L-6-v2)
- **Évaluation fine** de la pertinence
- **Fine-tuning** avec feedbacks utilisateurs
- **Amélioration continue** des performances

### 💾 Système d'Inférence et Feedback

- **Tracking automatique** de toutes les recommandations
- **Feedback simplifié** : like/dislike/click/view
- **Collection MongoDB** dédiée avec indexation
- **Analyse de performance** et métriques
- **Préparation fine-tuning** automatique

### 📊 API REST Complète

- **FastAPI** avec documentation interactive
- **Architecture MVC** propre et maintenable
- **Validation Pydantic** des données
- **Gestion d'erreurs** robuste
- **CORS configuré** pour intégration frontend

---

## 🏗️ Architecture

### Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Frontend)                         │
│                  Web App / Mobile App / API Client               │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Routes     │  │ Controllers  │  │   Services    │        │
│  │              │  │              │  │               │        │
│  │ - Workflow   │──│ - Workflow   │──│ - Workflow    │        │
│  │ - Crawler    │  │ - Crawler    │  │ - Crawler     │        │
│  │ - NLP        │  │ - NLP        │  │ - NLP         │        │
│  │ - Reranking  │  │ - Reranking  │  │ - Reranking   │        │
│  │ - Queries    │  │ - Queries    │  │ - Queries     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
└──────────────┬───────────────────────────┬─────────────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────┐  ┌────────────────────────────────┐
│      MONGODB             │  │    FAISS INDEX (Local)         │
│                          │  │                                │
│ Collections:             │  │ - Vector embeddings            │
│ - ressources_educatives  │  │ - Fast similarity search       │
│ - users_queries          │  │ - Persisted on disk            │
│ - inference              │  │                                │
│ - user_feedbacks         │  │                                │
└──────────────────────────┘  └────────────────────────────────┘
```

### Architecture MVC

```
src/
├── routes/              # Définition des endpoints API
│   ├── workflow_routes.py      # Route principale du workflow
│   ├── crawler_routes.py       # Routes de crawling
│   ├── nlp_routes.py           # Routes NLP/FAISS
│   └── reranking_routes.py     # Routes re-ranking
│
├── controllers/         # Logique de contrôle HTTP
│   ├── workflow_controller.py
│   ├── crawler_controller.py
│   └── ...
│
├── services/            # Logique métier
│   ├── workflow_service.py     # Orchestration globale
│   ├── crawler_service.py      # Crawling multi-sources
│   ├── nlp_service.py          # FAISS + embeddings
│   ├── reranking_service.py    # Cross-encoder
│   └── user_query_service.py   # Gestion requêtes
│
└── models/              # Modèles Pydantic
    ├── workflow_model.py
    ├── crawler_model.py
    └── ...
```

---

## 🔄 Workflow Global

### Vue d'Ensemble

Le **workflow global** est le cœur de l'application. Il orchestre 6 étapes pour transformer une question en liste de ressources classées.

```
┌────────────────────────────────────────────────────────┐
│  Question: "Comment apprendre le machine learning ?"   │
└────────────────────┬───────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │ 1️⃣ SAUVEGARDE QUESTION  │
        │                         │
        │ • Stockage MongoDB      │
        │ • Génération embedding  │
        │ • Détection langue      │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ 2️⃣ CRAWLING SOURCES     │
        │                         │
        │ • Wikipedia (FR/EN)     │
        │ • GitHub Repos          │
        │ • Medium Articles       │
        │ • Extraction métadonnées│
        │ • Génération embeddings │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ 3️⃣ INDEX FAISS          │
        │                         │
        │ • Chargement embeddings │
        │ • Construction index    │
        │ • Sauvegarde disque     │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ 4️⃣ RECHERCHE SEMANTIQUE │
        │                         │
        │ • Embedding question    │
        │ • Similarité cosine     │
        │ • Top 50 résultats      │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ 5️⃣ RE-RANKING           │
        │                         │
        │ • Cross-Encoder BERT    │
        │ • Évaluation fine       │
        │ • Top 10 finaux         │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │ 6️⃣ SAUVEGARDE INFERENCES│
        │                         │
        │ • Tracking recommandations │
        │ • Prêt pour feedbacks   │
        │ • Métriques performance │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   TOP 10 RESSOURCES     │
        │                         │
        │ • Titre, URL, Auteur    │
        │ • Scores détaillés      │
        │ • Mots-clés, Source     │
        │ • ID inférence          │
        └─────────────────────────┘
```

### Utilisation du Workflow

**Requête minimale :**
```bash
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Comment apprendre Python ?"
  }'
```

**Requête complète avec paramètres :**
```bash
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Deep learning tutorial",
    "max_par_site": 20,
    "sources": ["wikipedia", "github", "medium"],
    "langues": ["fr", "en"],
    "top_k_faiss": 50,
    "top_k_final": 10
  }'
```

**Exemple Python :**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/workflow/process",
    json={"question": "Comment utiliser TensorFlow ?"}
)

data = response.json()
print(f"✅ {data['total_resultats_final']} résultats en {data['duree_totale_secondes']}s")

for i, r in enumerate(data['resultats'], 1):
    print(f"{i}. {r['titre']} (score: {r['score_final']:.2f})")
    print(f"   {r['url']}")
```

### Format de Réponse

```json
{
  "question": "Comment apprendre le machine learning ?",
  "id_requete": "507f1f77bcf86cd799439011",
  "total_crawle": 45,
  "total_resultats_faiss": 50,
  "total_resultats_final": 10,
  "duree_crawl_secondes": 12.5,
  "duree_recherche_secondes": 0.3,
  "duree_reranking_secondes": 1.2,
  "duree_totale_secondes": 14.0,
  "resultats": [
    {
      "titre": "Introduction au Machine Learning",
      "url": "https://fr.wikipedia.org/wiki/Machine_learning",
      "auteur": "Wikipedia Contributors",
      "date": "2024-01-15",
      "score_faiss": 0.85,
      "score_reranking": 0.92,
      "score_final": 0.89,
      "mots_cles": ["machine learning", "IA", "apprentissage"],
      "source": "wikipedia",
      "id_inference": "507f1f77bcf86cd799439012"
    }
    // ... 9 autres ressources
  ],
  "sources_crawlees": ["wikipedia", "github", "medium"],
  "erreurs": []
}
```

➡️ **[Documentation complète du workflow](docs/WORKFLOW_GUIDE.md)**

---

## 📁 Structure du Projet

```
crawler-enduranker-api/
├── 📄 main.py                          # Point d'entrée de l'application
├── 📄 requirements.txt                 # Dépendances Python
├── 📄 docker-compose.yml               # Configuration Docker (MongoDB)
├── 📄 .env                            # Variables d'environnement
│
├── 📁 src/                            # Code source principal
│   ├── database.py                    # Configuration MongoDB
│   ├── utils.py                       # Utilitaires communs
│   │
│   ├── 📁 routes/                     # Endpoints API (FastAPI)
│   │   ├── workflow_routes.py         # 🔥 Route principale du workflow
│   │   ├── crawler_routes.py          # Routes de crawling
│   │   ├── nlp_routes.py              # Routes NLP/FAISS
│   │   ├── reranking_routes.py        # Routes re-ranking
│   │   └── user_query_routes.py       # Routes requêtes utilisateur
│   │
│   ├── 📁 controllers/                # Contrôleurs HTTP
│   │   ├── workflow_controller.py     # Contrôleur workflow
│   │   ├── crawler_controller.py      # Contrôleur crawler
│   │   ├── reranking_controller.py    # Contrôleur re-ranking
│   │   └── user_query_controller.py   # Contrôleur requêtes
│   │
│   ├── 📁 services/                   # Logique métier
│   │   ├── workflow_service.py        # 🎯 Orchestration workflow (6 étapes)
│   │   ├── crawler_service.py         # Crawling multi-sources
│   │   ├── nlp_service.py             # FAISS + Embeddings
│   │   ├── reranking_service.py       # Cross-Encoder + Fine-tuning
│   │   └── user_query_service.py      # Gestion requêtes utilisateur
│   │
│   └── 📁 models/                     # Modèles Pydantic (validation)
│       ├── workflow_model.py          # Modèles du workflow
│       ├── crawler_model.py           # Modèles de crawling
│       ├── reranking_model.py         # Modèles de re-ranking
│       └── user_query_model.py        # Modèles de requêtes
│
├── 📁 data/                           # Données persistantes
│   ├── faiss_index.index              # Index FAISS
│   └── faiss_index.ids                # IDs des ressources
│
├── 📁 models/                         # Modèles ML
│   └── cross_encoder_finetuned/       # Modèle BERT fine-tuné
│       ├── pytorch_model.bin          # Poids du modèle
│       ├── config.json                # Configuration
│       └── training_metadata.pkl      # Métadonnées d'entraînement
│
├── 📁 docs/                           # Documentation
│   ├── WORKFLOW_GUIDE.md              # 📖 Guide complet du workflow
│   ├── NLP_SERVICE.md                 # Documentation NLP/FAISS
│   └── RERANKING_SERVICE.md           # Documentation Re-ranking
│
├── 📁 notebooks/                      # Jupyter Notebooks
│   ├── fine_tune_cross_encoder.ipynb  # Fine-tuning du modèle
│   └── FINE_TUNING_GUIDE.md           # Guide de fine-tuning
│
├── 📁 public/                         # Fichiers statiques
│   └── index.html                     # Page d'accueil
│
└── 📁 scripts/                        # Scripts utilitaires
    ├── test_workflow.py               # Tests du workflow
    └── examples_workflow.sh           # Exemples curl
```

---

## 🚀 Installation

### Prérequis

- **Python 3.10+**
- **MongoDB 6.0+** (ou Docker)
- **8 GB RAM minimum** (16 GB recommandé pour le fine-tuning)
- **Connexion Internet** (pour le crawling)

### Installation Rapide

#### Option 1 : Avec Docker (Recommandé)

```bash
# 1. Cloner le repository
git clone <votre-repo-url>
cd crawler-enduranker-api

# 2. Démarrer MongoDB avec Docker
docker-compose up -d

# 3. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env si nécessaire

# 6. Démarrer l'API
python main.py
```

#### Option 2 : MongoDB Local

```bash
# 1-3. Même chose que l'option 1

# 4. Vérifier que MongoDB est en cours d'exécution
sudo systemctl status mongod
sudo systemctl start mongod  # Si nécessaire

# 5-6. Installer dépendances et démarrer
pip install -r requirements.txt
python main.py
```

### Configuration

#### Variables d'Environnement (.env)

```bash
# Application
APP_NAME=EduRanker Crawler API
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=eduranker_db

# FAISS
FAISS_INDEX_PATH=data/faiss_index

# Logging
LOG_LEVEL=INFO
```

### Vérification de l'Installation

```bash
# 1. Vérifier que l'API fonctionne
curl http://localhost:8000/health

# 2. Accéder à la documentation
# Ouvrir http://localhost:8000/docs dans votre navigateur

# 3. Tester le workflow
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment apprendre Python ?"}'
```

---

## 💻 Utilisation

### Démarrage Rapide

```bash
# Terminal 1 : Démarrer MongoDB (si Docker)
docker-compose up -d

# Terminal 2 : Démarrer l'API
python main.py

# Terminal 3 : Tester le workflow
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment apprendre Python ?"}'
```

### Exemples d'Utilisation

#### 1. Workflow Global (Recommandé)

```python
import requests

# Obtenir le top 10 pour une question
response = requests.post(
    "http://localhost:8000/api/workflow/process",
    json={
        "question": "Comment débuter en data science ?",
        "sources": ["wikipedia", "github"],
        "top_k_final": 10
    }
)

results = response.json()
print(f"✅ {results['total_resultats_final']} ressources trouvées")

for i, resource in enumerate(results['resultats'], 1):
    print(f"\n{i}. {resource['titre']}")
    print(f"   Score: {resource['score_final']:.3f}")
    print(f"   URL: {resource['url']}")
    print(f"   Source: {resource['source']}")
```

#### 2. Crawling Seul

```bash
curl -X POST "http://localhost:8000/api/crawler/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "TensorFlow tutorial",
    "max_par_site": 15,
    "sources": ["github", "medium"],
    "langues": ["en"]
  }'
```

#### 3. Recherche Sémantique

```bash
curl -X POST "http://localhost:8000/api/nlp/search" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "natural language processing",
    "top_k": 20
  }'
```

#### 4. Feedback sur une Recommandation

```bash
curl -X POST "http://localhost:8000/api/reranking/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "inference_id": "507f1f77bcf86cd799439011",
    "feedback_type": "positive"
  }'
```

---

## 📚 API Endpoints

### Workflow Global

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/workflow/process` | POST | 🔥 **Workflow complet** : crawling → recherche → re-ranking |
| `/api/workflow/health` | GET | Health check du workflow |

### Crawler

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/crawler/collect` | POST | Collecter des ressources depuis les sources |
| `/api/crawler/search` | POST | Rechercher dans les ressources collectées |
| `/api/crawler/stats` | GET | Statistiques du crawler |

### NLP & FAISS

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/nlp/search` | POST | Recherche sémantique avec FAISS |
| `/api/nlp/index/rebuild` | POST | Reconstruire l'index FAISS |
| `/api/nlp/stats` | GET | Statistiques de l'index |
| `/api/nlp/index/add` | POST | Ajouter des ressources à l'index |

### Re-ranking

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/reranking/search-with-reranking` | POST | Recherche + re-ranking automatique |
| `/api/reranking/rerank` | POST | Re-ranker des résultats existants |
| `/api/reranking/feedback` | POST | Soumettre un feedback utilisateur |
| `/api/reranking/fine-tune` | POST | Lancer le fine-tuning du modèle |
| `/api/reranking/inferences/{query_id}` | GET | Récupérer les inférences |

### Requêtes Utilisateur

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/queries/save` | POST | Sauvegarder une question utilisateur |
| `/api/queries/recent` | GET | Récupérer les requêtes récentes |
| `/api/queries/stats` | GET | Statistiques des requêtes |

### Documentation

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Page d'accueil |
| `http://localhost:8000/docs` | 📖 Documentation Swagger UI (interactive) |
| `http://localhost:8000/redoc` | Documentation ReDoc |
| `http://localhost:8000/health` | Health check API |

---

## 🛠️ Technologies

### Backend & API

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderne et performant
- **[Pydantic](https://docs.pydantic.dev/)** - Validation des données
- **[Uvicorn](https://www.uvicorn.org/)** - Serveur ASGI

### Base de Données

- **[MongoDB](https://www.mongodb.com/)** - Base NoSQL pour stockage flexible
- **[Motor](https://motor.readthedocs.io/)** - Driver MongoDB asynchrone
- **[PyMongo](https://pymongo.readthedocs.io/)** - Driver MongoDB

### Machine Learning & NLP

- **[Sentence-Transformers](https://www.sbert.net/)** - Embeddings sémantiques
  - Modèle: `all-MiniLM-L6-v2` (384 dimensions)
- **[FAISS](https://github.com/facebookresearch/faiss)** - Recherche vectorielle ultra-rapide
- **[Transformers](https://huggingface.co/transformers/)** (HuggingFace) - Cross-Encoder
  - Modèle: `ms-marco-MiniLM-L-6-v2`
- **[PyTorch](https://pytorch.org/)** - Framework deep learning

### Crawling & Web Scraping

- **[Requests](https://requests.readthedocs.io/)** - Requêtes HTTP
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** - Parsing HTML
- **Wikipedia API** - Accès aux articles Wikipedia
- **GitHub API** - Accès aux repositories

### Utilitaires

- **[Python-dotenv](https://github.com/theskumar/python-dotenv)** - Variables d'environnement
- **NumPy** - Calculs numériques
- **Pandas** - Analyse de données

---

## 📖 Documentation

### Guides Complets

| Document | Description | Temps de Lecture |
|----------|-------------|------------------|
| **[WORKFLOW_GUIDE.md](docs/WORKFLOW_GUIDE.md)** | 📖 Guide complet du workflow global | 30 min |
| **[NLP_SERVICE.md](docs/NLP_SERVICE.md)** | Documentation NLP et FAISS | 20 min |
| **[RERANKING_SERVICE.md](docs/RERANKING_SERVICE.md)** | Documentation Re-ranking | 20 min |
| **[FINE_TUNING_GUIDE.md](notebooks/FINE_TUNING_GUIDE.md)** | Guide de fine-tuning du modèle | 45 min |

### Quick Start

| Document | Description | Temps |
|----------|-------------|-------|
| **[QUICKSTART_WORKFLOW.md](QUICKSTART_WORKFLOW.md)** | Démarrage rapide workflow | 5 min |
| **[INSTALLATION_COMPLETE.md](INSTALLATION_COMPLETE.md)** | Installation complète | 10 min |
| **[SUMMARY.md](SUMMARY.md)** | Résumé du projet | 10 min |

### Fichiers Techniques

- `BUGFIX_INFERENCE.md` - Corrections de bugs
- `WORKFLOW_IMPLEMENTATION.md` - Détails d'implémentation
- `COMMANDES_ESSENTIELLES.sh` - Commandes utiles

---

## 🧪 Tests

### Tests Automatisés

```bash
# Test complet du workflow
python test_workflow.py

# Exemples variés (5 cas d'usage)
./examples_workflow.sh

# Commandes essentielles
./COMMANDES_ESSENTIELLES.sh
```

### Tests Manuels

```bash
# 1. Health Check
curl http://localhost:8000/health
curl http://localhost:8000/api/workflow/health

# 2. Test workflow simple
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{"question": "Python tutorial"}'

# 3. Test avec paramètres
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Deep learning for beginners",
    "max_par_site": 10,
    "sources": ["wikipedia"],
    "langues": ["en"],
    "top_k_final": 5
  }'
```

### Vérification MongoDB

```bash
# Se connecter à MongoDB
docker exec -it mongodb mongo eduranker_db
# ou
mongosh eduranker_db

# Commandes MongoDB
show collections
db.ressources_educatives.count()
db.users_queries.find().sort({date_creation:-1}).limit(5).pretty()
db.inference.find().sort({date_inference:-1}).limit(5).pretty()
```

---

## ⚡ Performances

### Temps d'Exécution

| Étape | Durée Typique | Notes |
|-------|---------------|-------|
| Sauvegarde question | < 0.1s | Quasi instantané |
| Crawling | 10-30s | Dépend des sources et du réseau |
| Index FAISS | 1-5s | Dépend du nombre de ressources |
| Recherche FAISS | 0.1-0.5s | Ultra-rapide (même 100k+ vecteurs) |
| Re-ranking | 1-3s | Dépend du top_k |
| Sauvegarde inférences | < 0.5s | Asynchrone |
| **TOTAL** | **12-40s** | Acceptable pour un workflow complet |

### Optimisations

#### Pour la Vitesse
```json
{
  "max_par_site": 10,
  "sources": ["wikipedia"],
  "top_k_faiss": 30,
  "top_k_final": 5
}
```

#### Pour la Précision
```json
{
  "max_par_site": 25,
  "sources": ["wikipedia", "github", "medium"],
  "top_k_faiss": 100,
  "top_k_final": 15
}
```

### Capacité

- **MongoDB** : Illimité (disque)
- **FAISS Index** : Jusqu'à 1M+ de vecteurs (16GB RAM)
- **Concurrent requests** : 100+ (avec Uvicorn workers)

---

## 💾 Base de Données MongoDB

### Collections

#### 1. `ressources_educatives`
Stocke toutes les ressources crawlées avec leurs embeddings.

```javascript
{
  "_id": ObjectId("..."),
  "titre": "Introduction au Machine Learning",
  "url": "https://...",
  "source": "wikipedia",
  "langue": "fr",
  "auteur": "Wikipedia Contributors",
  "date": "2024-01-15",
  "texte": "Le machine learning est...",
  "embedding": [0.1, -0.2, ...],  // 384 dimensions
  "popularite": 150,
  "type_ressource": "article",
  "mots_cles": ["ML", "IA"],
  "requete_originale": "machine learning",
  "date_collecte": ISODate("2024-01-20")
}
```

#### 2. `users_queries`
Stocke les questions des utilisateurs.

```javascript
{
  "_id": ObjectId("..."),
  "question": "Comment apprendre Python ?",
  "embedding": [0.15, -0.23, ...],  // 384 dimensions
  "langue_detectee": "fr",
  "date_creation": ISODate("2024-01-20")
}
```

#### 3. `inference`
Trackingdes recommandations et feedbacks.

```javascript
{
  "_id": ObjectId("..."),
  "user_query_id": "507f...",
  "resource_id": "507f...",
  "faiss_score": 0.85,
  "reranking_score": 0.92,
  "final_score": 0.89,
  "rank": 1,
  "feedback": "positive",  // ou null
  "date_inference": ISODate("2024-01-20"),
  "date_feedback": ISODate("2024-01-20"),
  "session_id": "user_123"
}
```

### Index MongoDB

Des index sont créés automatiquement pour optimiser les performances :

- `ressources_educatives` : `source`, `langue`, `requete_originale`
- `users_queries` : `date_creation`
- `inference` : `user_query_id`, `resource_id`, `feedback`, `session_id`, `date_inference`

---

## 🎯 Système d'Inférence et Feedback

### Fonctionnement

1. **Tracking Automatique** : Chaque recommandation est sauvegardée dans `inference`
2. **Feedback Utilisateur** : Les utilisateurs peuvent donner leur avis (positive/negative/click/view)
3. **Analyse** : Les données sont analysées pour comprendre les performances
4. **Fine-tuning** : Le modèle est amélioré avec les feedbacks positifs/négatifs

### Workflow Feedback

```
Recherche → Résultats avec inference_id → Utilisateur interagit → Feedback
                                                                      ↓
                                             MongoDB (inference collection)
                                                                      ↓
                                                Fine-tuning Périodique
                                                                      ↓
                                                  Modèle Amélioré
```

### Exemple Intégration Frontend

```javascript
// 1. Workflow complet
const response = await fetch('/api/workflow/process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    question: userInput,
    top_k_final: 10
  })
});

const data = await response.json();

// 2. Afficher résultats avec handlers de feedback
data.resultats.forEach(resource => {
  const card = createResourceCard(resource);
  
  // Bouton Like
  card.querySelector('.like-btn').onclick = async () => {
    await fetch('/api/reranking/feedback', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        inference_id: resource.id_inference,
        feedback_type: 'positive'
      })
    });
    showToast('Merci pour votre feedback !');
  };
  
  // Tracking des clics
  card.querySelector('.resource-link').onclick = async () => {
    await fetch('/api/reranking/feedback', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        inference_id: resource.id_inference,
        feedback_type: 'click'
      })
    });
  };
});
```

---

## 🔧 Fine-Tuning du Modèle

### Processus

1. **Collecter des feedbacks** (minimum 50-100)
2. **Lancer le fine-tuning** via API ou notebook
3. **Évaluer le nouveau modèle**
4. **Déployer en production**

### Via API

```bash
curl -X POST "http://localhost:8000/api/reranking/fine-tune?num_epochs=3" \
  -H "Content-Type: application/json"
```

### Via Notebook

```bash
jupyter notebook notebooks/fine_tune_cross_encoder.ipynb
```

Le notebook guide à travers :
- Chargement des données de feedback
- Préparation des paires (query, resource, label)
- Configuration du fine-tuning
- Entraînement du modèle
- Évaluation des performances
- Sauvegarde du modèle

### Métriques

Le système génère automatiquement :
- **Accuracy** : Précision globale
- **Precision/Recall** : Par classe (positive/negative)
- **F1-Score** : Mesure harmonique
- **Confusion Matrix** : Visualisation des erreurs
- **Courbe ROC** : Performance du classifieur

---

## 🚧 Déploiement

### Production

#### Option 1 : Docker (Recommandé)

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```bash
# Build et run
docker build -t eduranker-api .
docker run -p 8000:8000 --env-file .env eduranker-api
```

#### Option 2 : Serveur Linux

```bash
# Installer les dépendances système
sudo apt-get update
sudo apt-get install python3.10 python3-pip mongodb

# Déployer l'application
git clone <repo>
cd crawler-enduranker-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Utiliser systemd pour le démarrage automatique
sudo systemctl enable eduranker-api
sudo systemctl start eduranker-api
```

### Configuration Production

```env
# .env.production
DEBUG=False
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000

# Utiliser MongoDB Atlas ou serveur dédié
MONGODB_URL=mongodb://username:password@host:27017

# CORS spécifique
ALLOWED_ORIGINS=https://votre-frontend.com
```

---

## 🤝 Contributing

### Comment Contribuer

1. **Fork** le projet
2. **Créer une branche** : `git checkout -b feature/AmazingFeature`
3. **Commit** : `git commit -m 'Add AmazingFeature'`
4. **Push** : `git push origin feature/AmazingFeature`
5. **Pull Request**

### Standards de Code

- **PEP 8** : Style guide Python
- **Type hints** : Utiliser les annotations de types
- **Docstrings** : Documenter les fonctions
- **Tests** : Ajouter des tests pour les nouvelles features

---

## 📝 Roadmap

### Version 1.0 (Actuelle) ✅
- [x] Workflow global complet
- [x] Crawler multi-sources
- [x] Recherche FAISS
- [x] Re-ranking cross-encoder
- [x] Système d'inférence
- [x] Fine-tuning

### Version 1.1 (En Cours) 🚧
- [ ] Cache Redis pour performances
- [ ] Pagination des résultats
- [ ] Filtres avancés (date, source, langue)
- [ ] API rate limiting
- [ ] Webhooks pour notifications

### Version 2.0 (Futur) 🔮
- [ ] Support de nouvelles sources (Stack Overflow, arXiv, Coursera)
- [ ] Recommandations personnalisées par utilisateur
- [ ] Multi-modal (images, vidéos)
- [ ] GraphQL API
- [ ] Dashboard d'administration

---

## ❓ FAQ

### Q: Combien de temps prend le workflow ?
**R:** Entre 12 et 40 secondes selon les paramètres et la connexion internet.

### Q: Combien de ressources puis-je stocker ?
**R:** Illimité dans MongoDB. L'index FAISS peut gérer 1M+ de vecteurs avec 16GB RAM.

### Q: Le modèle s'améliore-t-il automatiquement ?
**R:** Non, le fine-tuning doit être lancé manuellement après collecte de feedbacks.

### Q: Puis-je ajouter mes propres sources ?
**R:** Oui, en créant un nouveau spider dans `src/services/crawler_service.py`.

### Q: Les embeddings sont-ils générés automatiquement ?
**R:** Oui, automatiquement lors du crawling avec sentence-transformers.

### Q: Puis-je utiliser un autre modèle de re-ranking ?
**R:** Oui, modifier `RERANKING_MODEL` dans le service de re-ranking.

### Q: Comment sauvegarder l'index FAISS ?
**R:** L'index est sauvegardé automatiquement dans `data/faiss_index`.

### Q: L'API est-elle prête pour la production ?
**R:** Oui, avec quelques ajustements (CORS, rate limiting, monitoring).

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👥 Auteurs

- **Équipe EduRanker** - Projet Master 2 Data Science
- **Cours** : INF5101 Traitement multimédia des données
- **Année** : 2024-2025

---

## 🙏 Remerciements

- **FastAPI** pour le framework web excellent
- **HuggingFace** pour les modèles pré-entraînés
- **Facebook AI** pour FAISS
- **MongoDB** pour la base de données
- **Communauté Open Source** pour tous les outils utilisés

---

## 📞 Support

### Documentation
- 📖 **Guides complets** : Dossier `/docs`
- 🌐 **API Docs** : http://localhost:8000/docs
- 📚 **Notebooks** : Dossier `/notebooks`

### Contact
- 📧 **Email** : eduranker@example.com
- 💬 **Issues** : [GitHub Issues](https://github.com/votre-repo/issues)
- 📝 **Wiki** : [GitHub Wiki](https://github.com/votre-repo/wiki)

### Liens Utiles
- 🔗 **Repository** : https://github.com/votre-repo
- 📊 **Documentation complète** : https://docs.eduranker.com
- 🎓 **Tutoriels** : https://tutorials.eduranker.com

---

<div align="center">

**⭐ Si ce projet vous aide, n'hésitez pas à mettre une étoile ! ⭐**

Made with ❤️ by EduRanker Team

</div>
