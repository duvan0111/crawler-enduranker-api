# 🎉 Intégration YouTube - Résumé

## ✅ Ce qui a été implémenté

### 1. **Méthode de collecte YouTube** (`_collecter_youtube`)
   - Recherche de vidéos éducatives via YouTube Data API v3
   - Support multilingue (français/anglais)
   - Filtres automatiques (durée, SafeSearch, pertinence)
   - Collecte des métadonnées complètes (vues, likes, tags)
   - Génération automatique d'embeddings (384 dimensions)

### 2. **Configuration**
   - Variable d'environnement `YOUTUBE_API_KEY`
   - Détection automatique de la clé API
   - Désactivation gracieuse si clé manquante
   - Documentation dans `.env.example`

### 3. **Intégration dans le workflow**
   - YouTube ajouté automatiquement dans les sources par défaut
   - Compatible avec la collecte multi-sources
   - Sauvegarde automatique dans MongoDB
   - Indexation FAISS automatique

### 4. **Documentation complète**
   - `docs/YOUTUBE_INTEGRATION.md` - Guide technique complet
   - `docs/YOUTUBE_SETUP.md` - Guide de configuration pas à pas
   - `README.md` - Mise à jour avec mention YouTube
   - `.env.example` - Configuration documentée

### 5. **Script de test**
   - `test_youtube_integration.py` - Tests automatisés
   - Vérification de la clé API
   - Tests de collecte (YouTube seul et multi-sources)
   - Vérification de la sauvegarde MongoDB

## 📊 Données collectées par vidéo

```python
{
    "titre": "Machine Learning Tutorial for Beginners",
    "url": "https://www.youtube.com/watch?v=abc123",
    "source": "youtube",
    "langue": "en",
    "auteur": "freeCodeCamp.org",
    "date": "2024-01-15T10:30:00Z",
    "texte": "Machine Learning Tutorial... [titre + description]",
    "resume": "Learn machine learning from scratch...",
    "embedding": [0.123, -0.456, ...],  # 384 dimensions
    "popularite": 2500000,  # vues + (likes × 10)
    "type_ressource": "video",
    "mots_cles": ["machine learning", "tutorial", "python"],
    "requete_originale": "machine learning",
    "date_collecte": "2024-12-11T15:30:00"
}
```

## 🚀 Comment utiliser

### Via le code Python

```python
from src.services.crawler_service import SimpleCrawlerService

crawler = SimpleCrawlerService(mongodb_url, mongodb_db)

# YouTube uniquement
resultats = await crawler.collecter_ressources(
    question="Python machine learning",
    max_par_site=10,
    sources=['youtube']
)

# Multi-sources (incluant YouTube)
resultats = await crawler.collecter_ressources(
    question="Deep learning tutorial",
    max_par_site=5,
    sources=['github', 'youtube', 'wikipedia']
)
```

### Via l'API REST

```bash
# Démarrer le serveur
python main.py

# Collecter depuis YouTube
curl -X POST "http://localhost:8000/api/crawler/collecter" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Python pandas tutorial",
    "max_par_site": 10,
    "sources": ["youtube"]
  }'

# Workflow complet avec YouTube
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Comment apprendre le machine learning ?",
    "max_par_site": 5
  }'
```

### Via l'interface Swagger

1. Ouvrir http://localhost:8000/docs
2. Tester **POST /api/crawler/collecter**
3. Inclure `"youtube"` dans `sources`

## 📝 Étapes pour commencer

### 1. Obtenir une clé API (5 minutes)
   
   ➡️ Voir le guide détaillé: `docs/YOUTUBE_SETUP.md`

   Résumé rapide:
   - Créer un compte Google Cloud (gratuit)
   - Créer un projet
   - Activer YouTube Data API v3
   - Créer une clé API
   - Copier la clé

### 2. Configurer le projet

   ```bash
   # Copier le fichier d'exemple
   cp .env.example .env
   
   # Éditer .env et ajouter
   # YOUTUBE_API_KEY=votre_cle_api_ici
   nano .env
   ```

### 3. Tester l'intégration

   ```bash
   # Lancer le script de test
   python test_youtube_integration.py
   ```

   Résultat attendu:
   ```
   ✅ Clé API trouvée: AIzaSyD...xyz123
   ✅ Service crawler initialisé
   ✅ Collecte terminée en 3.45s
   📹 Vidéos collectées: 10
   ```

### 4. Utiliser dans votre application

   ```python
   # YouTube est automatiquement inclus si clé API présente
   resultats = await crawler_service.collecter_ressources(
       question="votre question",
       max_par_site=10
   )
   ```

## 💰 Quotas et coûts

### Gratuit
- ✅ 10,000 unités/jour
- ✅ Pas de carte bancaire requise
- ✅ ~90 recherches complètes/jour

### Consommation

| Action | Unités | Fréquence possible |
|--------|--------|-------------------|
| Recherche 5 vidéos | ~105 | ~95 fois/jour |
| Recherche 10 vidéos | ~110 | ~90 fois/jour |
| Workflow complet | ~110-150 | ~70-90 fois/jour |

### Monitoring
- Dashboard: https://console.cloud.google.com/apis/dashboard
- Utilisation en temps réel
- Alertes configurables

## 🎯 Avantages pour EduRanker

### 1. **Diversité de contenu**
   - Texte (Wikipedia, GitHub, Medium)
   - Vidéo (YouTube) 🆕
   - Format adapté à différents styles d'apprentissage

### 2. **Qualité des ressources**
   - Métriques de popularité (vues, likes)
   - Filtres de durée (vidéos moyennes = contenu structuré)
   - SafeSearch activé (contenu approprié)

### 3. **Pertinence améliorée**
   - Embeddings sur titre + description
   - Tags comme mots-clés
   - Recherche multilingue

### 4. **Engagement utilisateur**
   - Format vidéo très apprécié
   - Liens directs vers YouTube
   - Métadonnées riches (auteur, date, etc.)

### 5. **Scalabilité**
   - API officielle stable
   - Quotas généreux (extensibles)
   - Cache MongoDB automatique

## 📚 Fichiers modifiés/créés

### Modifiés
- ✅ `src/services/crawler_service.py` - Ajout méthode `_collecter_youtube()`
- ✅ `.env.example` - Documentation YOUTUBE_API_KEY
- ✅ `README.md` - Mention de YouTube

### Créés
- ✅ `docs/YOUTUBE_INTEGRATION.md` - Guide technique complet
- ✅ `docs/YOUTUBE_SETUP.md` - Guide de configuration détaillé
- ✅ `test_youtube_integration.py` - Script de test automatisé

## 🔧 Dépannage rapide

### Problème: "YOUTUBE_API_KEY non configurée"
```bash
# Solution: Ajouter la clé dans .env
echo "YOUTUBE_API_KEY=votre_cle" >> .env
```

### Problème: "API key not valid"
- Vérifier que YouTube Data API v3 est activée
- Vérifier que la clé est correcte
- Vérifier les restrictions de clé (si configurées)

### Problème: "Quota exceeded"
- Attendre 24h (reset à minuit PST)
- Réduire `max_par_site`
- Utiliser le cache MongoDB (éviter requêtes dupliquées)

### Problème: Aucune vidéo collectée
- Essayer avec une question plus générique
- Tester avec `langues=['en']` uniquement
- Vérifier les logs: `tail -f logs/app.log`

## 📖 Ressources

- [Guide d'intégration complet](docs/YOUTUBE_INTEGRATION.md)
- [Guide de configuration](docs/YOUTUBE_SETUP.md)
- [YouTube Data API Docs](https://developers.google.com/youtube/v3)
- [Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)

## ✨ Prochaines étapes suggérées

1. **Obtenir votre clé API** (5 min)
2. **Tester avec le script** `python test_youtube_integration.py`
3. **Intégrer dans votre workflow**
4. **Analyser les résultats** avec le système de ranking

---

**L'intégration YouTube est prête à être utilisée! 🎥🚀**

Pour toute question, consulter la documentation dans `docs/`.
