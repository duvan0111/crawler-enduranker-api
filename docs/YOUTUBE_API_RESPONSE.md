# Exemple de réponse API - Collecte YouTube

## Requête

```bash
POST http://localhost:8000/api/crawler/collecter
Content-Type: application/json

{
  "question": "Python machine learning tutorial",
  "max_par_site": 5,
  "sources": ["youtube"],
  "langues": ["en"]
}
```

## Réponse (200 OK)

```json
{
  "requete": "Python machine learning tutorial",
  "debut_collecte": "2024-12-11T15:30:00.123456",
  "fin_collecte": "2024-12-11T15:30:03.567890",
  "duree_collecte_secondes": 3.44,
  "sources_utilisees": ["youtube"],
  "max_par_site": 5,
  "total_collecte": 5,
  "resultats_par_source": {
    "youtube": {
      "statut": "succès",
      "nb_ressources": 5,
      "nb_sauvegardes": 5,
      "timestamp": "2024-12-11T15:30:03.567890"
    }
  },
  "erreurs": [],
  "ressources": [
    {
      "titre": "Machine Learning Tutorial for Beginners - Full Course",
      "url": "https://www.youtube.com/watch?v=gmvvaobm7eQ",
      "source": "youtube",
      "langue": "en",
      "auteur": "freeCodeCamp.org",
      "date": "2023-11-15T10:00:00Z",
      "texte": "Machine Learning Tutorial for Beginners - Full Course. This comprehensive machine learning tutorial covers all the fundamental concepts you need to get started with ML. Topics include supervised learning, unsupervised learning, neural networks, and practical implementations in Python.",
      "resume": "This comprehensive machine learning tutorial covers all the fundamental concepts you need to get started with ML. Topics include supervised learning, unsupervised learning, neural networks, and practical implementations in Python.",
      "embedding": [
        0.0234, -0.0156, 0.0789, -0.0345, 0.0512,
        "... (384 dimensions total)"
      ],
      "popularite": 2850000,
      "type_ressource": "video",
      "mots_cles": [
        "machine learning",
        "python",
        "tutorial",
        "beginner",
        "ai"
      ],
      "requete_originale": "Python machine learning tutorial",
      "date_collecte": "2024-12-11T15:30:02.123456"
    },
    {
      "titre": "Python Machine Learning Tutorial (Data Science)",
      "url": "https://www.youtube.com/watch?v=7eh4d6sabA0",
      "source": "youtube",
      "langue": "en",
      "auteur": "Programming with Mosh",
      "date": "2024-05-20T14:30:00Z",
      "texte": "Python Machine Learning Tutorial (Data Science). Learn machine learning with Python in this complete tutorial. We'll cover data preprocessing, model training, evaluation, and deployment using popular libraries like scikit-learn and pandas.",
      "resume": "Learn machine learning with Python in this complete tutorial. We'll cover data preprocessing, model training, evaluation, and deployment using popular libraries like scikit-learn and pandas.",
      "embedding": [
        0.0198, -0.0223, 0.0654, -0.0289, 0.0467,
        "... (384 dimensions total)"
      ],
      "popularite": 1560000,
      "type_ressource": "video",
      "mots_cles": [
        "python",
        "machine learning",
        "data science",
        "scikit-learn"
      ],
      "requete_originale": "Python machine learning tutorial",
      "date_collecte": "2024-12-11T15:30:02.345678"
    },
    {
      "titre": "Machine Learning with Python - Crash Course",
      "url": "https://www.youtube.com/watch?v=45ryDIPHdGg",
      "source": "youtube",
      "langue": "en",
      "auteur": "Tech With Tim",
      "date": "2024-08-10T09:15:00Z",
      "texte": "Machine Learning with Python - Crash Course. In this crash course, you'll learn the basics of machine learning using Python. Perfect for beginners who want to understand ML concepts quickly.",
      "resume": "In this crash course, you'll learn the basics of machine learning using Python. Perfect for beginners who want to understand ML concepts quickly.",
      "embedding": [
        0.0167, -0.0134, 0.0723, -0.0312, 0.0543,
        "... (384 dimensions total)"
      ],
      "popularite": 987500,
      "type_ressource": "video",
      "mots_cles": [
        "machine learning",
        "python",
        "crash course",
        "programming"
      ],
      "requete_originale": "Python machine learning tutorial",
      "date_collecte": "2024-12-11T15:30:02.567890"
    },
    {
      "titre": "Python for Machine Learning - Complete Beginner's Guide",
      "url": "https://www.youtube.com/watch?v=OGxgnH8y2NM",
      "source": "youtube",
      "langue": "en",
      "auteur": "Corey Schafer",
      "date": "2024-03-25T11:00:00Z",
      "texte": "Python for Machine Learning - Complete Beginner's Guide. This guide teaches you everything you need to know about using Python for machine learning, from installation to building your first model.",
      "resume": "This guide teaches you everything you need to know about using Python for machine learning, from installation to building your first model.",
      "embedding": [
        0.0189, -0.0201, 0.0698, -0.0278, 0.0498,
        "... (384 dimensions total)"
      ],
      "popularite": 654300,
      "type_ressource": "video",
      "mots_cles": [
        "python",
        "machine learning",
        "beginner guide",
        "tutorial"
      ],
      "requete_originale": "Python machine learning tutorial",
      "date_collecte": "2024-12-11T15:30:02.789012"
    },
    {
      "titre": "Intro to Machine Learning with Python and Scikit-Learn",
      "url": "https://www.youtube.com/watch?v=hd1W4CyPX58",
      "source": "youtube",
      "langue": "en",
      "auteur": "Sentdex",
      "date": "2024-06-18T16:45:00Z",
      "texte": "Intro to Machine Learning with Python and Scikit-Learn. Learn the fundamentals of machine learning using Python's most popular ML library, scikit-learn. Hands-on examples included.",
      "resume": "Learn the fundamentals of machine learning using Python's most popular ML library, scikit-learn. Hands-on examples included.",
      "embedding": [
        0.0212, -0.0178, 0.0734, -0.0301, 0.0521,
        "... (384 dimensions total)"
      ],
      "popularite": 432100,
      "type_ressource": "video",
      "mots_cles": [
        "machine learning",
        "python",
        "scikit-learn",
        "introduction"
      ],
      "requete_originale": "Python machine learning tutorial",
      "date_collecte": "2024-12-11T15:30:03.012345"
    }
  ]
}
```

## Structure de la réponse

### Métadonnées de collecte

| Champ | Type | Description |
|-------|------|-------------|
| `requete` | string | Question originale de l'utilisateur |
| `debut_collecte` | string (ISO 8601) | Date/heure de début |
| `fin_collecte` | string (ISO 8601) | Date/heure de fin |
| `duree_collecte_secondes` | float | Durée totale en secondes |
| `sources_utilisees` | array | Liste des sources interrogées |
| `max_par_site` | integer | Limite de résultats par source |
| `total_collecte` | integer | Nombre total de ressources collectées |

### Résultats par source

| Champ | Type | Description |
|-------|------|-------------|
| `statut` | string | "succès" ou "erreur" |
| `nb_ressources` | integer | Nombre de ressources collectées |
| `nb_sauvegardes` | integer | Nombre sauvegardées dans MongoDB |
| `timestamp` | string (ISO 8601) | Date/heure de collecte |

### Structure d'une ressource YouTube

| Champ | Type | Description |
|-------|------|-------------|
| `titre` | string | Titre de la vidéo |
| `url` | string | URL YouTube complète |
| `source` | string | Toujours "youtube" |
| `langue` | string | Code langue (en, fr) |
| `auteur` | string | Nom de la chaîne YouTube |
| `date` | string (ISO 8601) | Date de publication |
| `texte` | string | Titre + description (pour embedding) |
| `resume` | string | Description (max 500 caractères) |
| `embedding` | array[float] | Vecteur 384 dimensions |
| `popularite` | integer | Vues + (Likes × 10) |
| `type_ressource` | string | Toujours "video" |
| `mots_cles` | array[string] | Tags de la vidéo |
| `requete_originale` | string | Question de recherche |
| `date_collecte` | string (ISO 8601) | Date de collecte |

## Codes de statut HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Collecte réussie |
| 400 | Bad Request | Paramètres invalides |
| 500 | Internal Server Error | Erreur serveur |

## Exemples d'erreurs

### Clé API manquante

```json
{
  "requete": "Python machine learning tutorial",
  "debut_collecte": "2024-12-11T15:30:00.123456",
  "fin_collecte": "2024-12-11T15:30:01.234567",
  "duree_collecte_secondes": 1.11,
  "sources_utilisees": ["youtube"],
  "max_par_site": 5,
  "total_collecte": 0,
  "resultats_par_source": {
    "youtube": {
      "statut": "erreur",
      "erreur": "YOUTUBE_API_KEY non configurée",
      "nb_ressources": 0,
      "timestamp": "2024-12-11T15:30:01.234567"
    }
  },
  "erreurs": ["Erreur avec youtube: YOUTUBE_API_KEY non configurée"],
  "ressources": []
}
```

### Quota dépassé

```json
{
  "requete": "Python machine learning tutorial",
  "debut_collecte": "2024-12-11T15:30:00.123456",
  "fin_collecte": "2024-12-11T15:30:02.345678",
  "duree_collecte_secondes": 2.22,
  "sources_utilisees": ["youtube"],
  "max_par_site": 5,
  "total_collecte": 0,
  "resultats_par_source": {
    "youtube": {
      "statut": "erreur",
      "erreur": "403 Client Error: Forbidden - Quota exceeded",
      "nb_ressources": 0,
      "timestamp": "2024-12-11T15:30:02.345678"
    }
  },
  "erreurs": ["Erreur avec youtube: 403 Client Error: Forbidden - Quota exceeded"],
  "ressources": []
}
```

## Utilisation des données

### 1. Afficher les vidéos dans une interface

```javascript
// Frontend JavaScript
const response = await fetch('http://localhost:8000/api/crawler/collecter', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: 'Python machine learning tutorial',
    max_par_site: 5,
    sources: ['youtube']
  })
});

const data = await response.json();

data.ressources.forEach(video => {
  console.log(`📹 ${video.titre}`);
  console.log(`   Par: ${video.auteur}`);
  console.log(`   Vues: ${video.popularite.toLocaleString()}`);
  console.log(`   URL: ${video.url}`);
});
```

### 2. Recherche sémantique avec les embeddings

```python
# Backend Python
from src.services.nlp_service import get_nlp_service

nlp_service = get_nlp_service(mongodb_url, mongodb_db)

# Rechercher les vidéos similaires sémantiquement
resultats = await nlp_service.rechercher_avec_faiss(
    question="deep learning neural networks",
    top_k=10
)

# Filtrer uniquement les vidéos YouTube
videos = [r for r in resultats if r.source == 'youtube']
```

### 3. Re-ranking avec cross-encoder

```python
from src.services.reranking_service import get_reranking_service

reranking_service = get_reranking_service(mongodb_url, mongodb_db)

# Re-classer les vidéos par pertinence fine
resultats_reranked = await reranking_service.reranker_resultats(
    question="Python machine learning tutorial",
    resultats_initiaux=data['ressources']
)

# Top 3 vidéos les plus pertinentes
top_videos = resultats_reranked[:3]
```

## Performance

### Temps de réponse typiques

| Nombre de vidéos | Temps approximatif |
|------------------|-------------------|
| 5 vidéos | 2-4 secondes |
| 10 vidéos | 3-5 secondes |
| 15 vidéos | 4-6 secondes |

### Facteurs impactant la performance

- **Délais API** : 1s entre recherche + 0.5s pour détails
- **Génération embeddings** : ~50ms par vidéo
- **Sauvegarde MongoDB** : ~10ms par vidéo
- **Réseau** : Latence vers YouTube API

### Optimisations possibles

1. **Parallélisation** : Collecter depuis plusieurs langues en parallèle
2. **Cache** : Éviter les requêtes dupliquées (déjà implémenté)
3. **Réduction** : Limiter `max_par_site` pour réponses plus rapides
