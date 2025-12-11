# 🎥 Intégration YouTube Data API v3

## Vue d'ensemble

L'API YouTube Data API v3 est intégrée dans le service de crawling pour collecter des vidéos éducatives gratuitement avec des quotas généreux.

## Caractéristiques

✅ **Gratuit** avec quotas quotidiens  
✅ **10,000 unités par jour** par défaut (extensible sur demande)  
✅ **Recherche de vidéos** : ~100 unités par requête  
✅ **Détails des vidéos** : ~1 unité par requête  
✅ **Pas de carte bancaire** requise pour commencer

## Configuration

### 1. Obtenir une clé API YouTube

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un nouveau projet (ou utiliser un existant)
3. Activer **YouTube Data API v3** :
   - Menu Navigation → APIs & Services → Library
   - Rechercher "YouTube Data API v3"
   - Cliquer sur "Enable"
4. Créer des identifiants :
   - APIs & Services → Credentials
   - Create Credentials → API key
   - Copier la clé générée

### 2. Configurer la clé dans le projet

Ajouter la clé dans votre fichier `.env` :

```bash
YOUTUBE_API_KEY=AIzaSy...votre_cle_api
```

### 3. Vérifier l'intégration

Le service détectera automatiquement la clé API et activera YouTube dans les sources disponibles.

## Utilisation

### Collecte automatique

YouTube est inclus par défaut dans les sources si la clé API est configurée :

```python
# Collecte depuis toutes les sources (incluant YouTube)
resultats = await crawler_service.collecter_ressources(
    question="Python machine learning",
    max_par_site=10
)
```

### Collecte YouTube uniquement

```python
resultats = await crawler_service.collecter_ressources(
    question="Deep learning tutorial",
    max_par_site=15,
    sources=['youtube']
)
```

### Via l'API REST

```bash
# Collecte incluant YouTube
curl -X POST "http://localhost:8000/api/crawler/collecter" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Python pandas tutorial",
    "max_par_site": 10,
    "sources": ["youtube", "github", "wikipedia"]
  }'
```

## Données collectées

Pour chaque vidéo YouTube, le système collecte :

- **Titre** : Titre de la vidéo
- **URL** : Lien direct vers la vidéo
- **Description** : Description complète
- **Auteur** : Nom de la chaîne
- **Date** : Date de publication
- **Popularité** : Vues + (Likes × 10)
- **Langue** : Langue de la vidéo (fr/en)
- **Tags** : Mots-clés associés
- **Embedding** : Vecteur sémantique (384 dimensions)

## Filtres appliqués

Le service applique automatiquement des filtres pour des résultats éducatifs optimaux :

- ✅ **Durée** : Vidéos moyennes (4-20 minutes)
- ✅ **Pertinence** : Tri par pertinence avec le sujet
- ✅ **Recherche** : Inclut automatiquement "tutorial education"
- ✅ **Sécurité** : SafeSearch strict activé
- ✅ **Langue** : Support français et anglais

## Gestion des quotas

### Consommation des unités

| Opération | Coût en unités |
|-----------|----------------|
| Recherche (search) | 100 unités |
| Détails vidéo (videos) | 1 unité par vidéo |
| **Total par collecte** | ~110-120 unités |

### Optimisation

Avec 10,000 unités/jour, vous pouvez effectuer :
- **~90 recherches complètes** par jour
- **~1000 requêtes de détails** par jour

### Monitoring

Vérifier votre quota actuel sur [Google Cloud Console](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas).

## Exemples de résultats

### Recherche "machine learning"

```json
{
  "titre": "Machine Learning Tutorial for Beginners",
  "url": "https://www.youtube.com/watch?v=ABC123",
  "source": "youtube",
  "langue": "en",
  "auteur": "freeCodeCamp.org",
  "popularite": 2500000,
  "type_ressource": "video",
  "texte": "Complete machine learning tutorial covering...",
  "resume": "Learn machine learning from scratch...",
  "mots_cles": ["machine learning", "tutorial", "python", "AI"],
  "embedding": [0.123, -0.456, ...]
}
```

## Gestion des erreurs

### Pas de clé API

```
⚠️  YOUTUBE_API_KEY non configurée - YouTube sera désactivé
```

### Quota dépassé

```json
{
  "error": {
    "code": 403,
    "message": "The request cannot be completed because you have exceeded your quota."
  }
}
```

**Solution** : Attendre le lendemain (reset à minuit PST) ou demander une augmentation de quota.

### Clé API invalide

```
⚠️  Erreur YouTube: 400 Client Error: Bad Request
```

**Solution** : Vérifier que la clé API est correcte et que YouTube Data API v3 est activée.

## Bonnes pratiques

### 1. Limiter les résultats

```python
# Collecter 5 vidéos par recherche au lieu de 10
resultats = await crawler_service.collecter_ressources(
    question="Python tutorial",
    max_par_site=5,
    sources=['youtube']
)
```

### 2. Cache des résultats

Les résultats sont automatiquement sauvegardés dans MongoDB et indexés dans FAISS, évitant les requêtes dupliquées.

### 3. Délais entre requêtes

Le service applique automatiquement des délais (1s entre recherches) pour respecter les limites de l'API.

## Avantages pour EduRanker

✅ **Contenu multimédia** : Diversité des formats d'apprentissage  
✅ **Popularité** : Métriques de qualité (vues, likes)  
✅ **Actualité** : Contenu récent et à jour  
✅ **Engagement** : Commentaires et interactions disponibles  
✅ **Gratuit** : Pas de coût jusqu'à 10,000 unités/jour

## Ressources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [Python Client Library](https://github.com/googleapis/google-api-python-client)
- [API Explorer](https://developers.google.com/youtube/v3/docs)

## Support

Pour toute question ou problème :
1. Vérifier les logs du service
2. Consulter les quotas sur Google Cloud Console
3. Tester avec l'API Explorer de Google
