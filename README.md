# EduRanker Crawler API

Backend FastAPI pour le projet EduRanker avec système de crawling intégré.

## 🎯 Fonctionnalités

- **API REST complète** avec FastAPI
- **Crawler de ressources éducatives** depuis Wikipedia, GitHub, Medium
- **Base de données MongoDB** pour le stockage
- **Documentation interactive** avec Swagger UI
- **Architecture MVC** (Models, Views, Controllers)

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
