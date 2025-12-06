# Service NLP avec FAISS - Documentation

## Vue d'ensemble

Le service NLP implémente un système de recherche sémantique basé sur FAISS (Facebook AI Similarity Search) pour indexer et rechercher efficacement des ressources éducatives en utilisant leurs embeddings vectoriels.

## Architecture

### Composants principaux

1. **NLPService** (`src/services/nlp_service.py`)
   - Génération d'embeddings avec sentence-transformers
   - Indexation FAISS (384 dimensions)
   - Recherche sémantique
   - Gestion de la persistance de l'index

2. **Routes API** (`src/routes/nlp_routes.py`)
   - `/api/nlp/recherche-semantique` - Recherche sémantique
   - `/api/nlp/statistiques-index` - Statistiques de l'index
   - `/api/nlp/reconstruire-index` - Reconstruction manuelle
   - `/api/nlp/ajouter-ressources` - Ajout manuel de ressources
   - `/api/nlp/generer-embedding` - Test de génération d'embedding

3. **Intégration au cycle de vie** (`main.py`)
   - Chargement/reconstruction de l'index au démarrage
   - Mise à jour automatique après chaque crawl

## Fonctionnement

### 1. Démarrage de l'application

Au démarrage, le système :
1. Initialise le service NLP
2. Essaie de charger l'index FAISS sauvegardé
3. Si aucun index n'existe, reconstruit depuis MongoDB
4. Affiche les statistiques de l'index

```python
# Dans main.py - lifespan
nlp_service = get_nlp_service(mongodb_url, mongodb_db, index_path)

if nlp_service.charger_index():
    # Index chargé depuis le disque
else:
    # Reconstruction depuis MongoDB
    await nlp_service.reconstruire_index_depuis_bd()
```

### 2. Crawl de nouvelles ressources

Lorsque de nouvelles ressources sont collectées :
1. Les embeddings sont générés avec sentence-transformers
2. Les ressources sont sauvegardées dans MongoDB
3. L'index FAISS est automatiquement mis à jour

```python
# Dans crawler_service.py - _sauvegarder_mongodb
if nouveaux_ids:
    nlp_service = get_nlp_service(...)
    await nlp_service.ajouter_ressources_a_index(nouveaux_ids)
```

### 3. Recherche sémantique

Pour rechercher des ressources :
1. La question utilisateur est vectorisée
2. FAISS trouve les k plus proches voisins
3. Les ressources complètes sont récupérées depuis MongoDB

```python
# Exemple d'utilisation
resultats = await nlp_service.recherche_et_recuperer_ressources(
    question="machine learning en éducation",
    top_k=10
)
```

## Modèle d'embeddings

- **Modèle** : sentence-transformers/all-MiniLM-L6-v2
- **Dimensions** : 384
- **Normalisation** : Embeddings normalisés pour similarité cosine
- **Index FAISS** : IndexFlatIP (Inner Product)

## API Endpoints

### Recherche sémantique

```bash
POST /api/nlp/recherche-semantique?question=machine learning&top_k=10
```

**Réponse** :
```json
{
  "status": "success",
  "question": "machine learning",
  "nb_resultats": 10,
  "resultats": [
    {
      "titre": "Introduction au Machine Learning",
      "url": "https://...",
      "source": "wikipedia",
      "texte": "...",
      "score_similarite": 0.85,
      ...
    }
  ]
}
```

### Statistiques de l'index

```bash
GET /api/nlp/statistiques-index
```

**Réponse** :
```json
{
  "status": "success",
  "statistiques": {
    "index_existe": true,
    "nb_vecteurs": 150,
    "dimension": 384,
    "type_index": "IndexFlatIP (Inner Product)",
    "nb_resource_ids": 150
  }
}
```

### Reconstruction manuelle

```bash
POST /api/nlp/reconstruire-index
```

Utile pour :
- Réparer un index corrompu
- Recharger après une modification manuelle de la BD
- Maintenance

## Persistance

### Fichiers sauvegardés

- `data/faiss_index.index` : Index FAISS binaire
- `data/faiss_index.ids` : Liste des IDs MongoDB (pickle)

### Sauvegarde automatique

L'index est automatiquement sauvegardé :
- Après reconstruction
- Après ajout de nouvelles ressources

## Performance

### Recherche
- **Complexité** : O(n) avec IndexFlatIP (recherche exhaustive)
- **Précision** : Maximale (pas d'approximation)
- **Vitesse** : ~1ms pour 1000 vecteurs

### Optimisations possibles

Pour de très grandes bases (>100k vecteurs) :
- Utiliser IndexIVFFlat (quantization)
- Utiliser IndexHNSW (graphes)
- GPU avec faiss-gpu

## Exemple d'utilisation complète

### 1. Démarrer l'application

```bash
uvicorn main:app --reload
```

L'index est chargé/reconstruit automatiquement.

### 2. Crawler des ressources

```bash
POST /api/crawler/collecter
{
  "question": "deep learning",
  "max_par_site": 15
}
```

Les nouvelles ressources sont automatiquement indexées.

### 3. Rechercher sémantiquement

```bash
POST /api/nlp/recherche-semantique?question=apprentissage profond&top_k=5
```

Retourne les 5 ressources les plus similaires, même si la question est en français et les ressources en anglais.

## Variables d'environnement

```bash
# Chemin de l'index FAISS
FAISS_INDEX_PATH=data/faiss_index

# MongoDB (déjà existant)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=eduranker_db
```

## Logging

Le service NLP utilise le logger Python standard :

```python
import logging
logger = logging.getLogger(__name__)
```

Messages clés :
- 📥 Chargement du modèle
- ✅ Succès des opérations
- 🔄 Reconstruction de l'index
- 🔍 Résultats de recherche
- ❌ Erreurs

## Tests

### Tester la génération d'embedding

```bash
POST /api/nlp/generer-embedding?texte=hello world
```

### Tester la recherche

```bash
POST /api/nlp/recherche-semantique?question=test&top_k=5
```

### Vérifier les statistiques

```bash
GET /api/nlp/statistiques-index
```

## Maintenance

### Reconstruire l'index

Si l'index semble corrompu ou obsolète :

```bash
POST /api/nlp/reconstruire-index
```

### Sauvegarder l'index

L'index est sauvegardé automatiquement, mais vous pouvez aussi :

```bash
# Copier les fichiers
cp data/faiss_index.index data/backups/
cp data/faiss_index.ids data/backups/
```

## Dépannage

### L'index est vide au démarrage

1. Vérifier que MongoDB contient des ressources avec embeddings
2. Vérifier les logs au démarrage
3. Forcer la reconstruction avec `/api/nlp/reconstruire-index`

### Résultats de recherche non pertinents

1. Vérifier la qualité des embeddings générés
2. Vérifier que les textes des ressources sont significatifs
3. Augmenter `top_k` pour plus de résultats

### Performance lente

1. Vérifier le nombre de vecteurs dans l'index
2. Considérer une mise à niveau vers IndexIVF pour >100k vecteurs
3. Utiliser faiss-gpu pour de très grandes bases

## Évolutions futures

1. **Clustering** : Regrouper les ressources similaires
2. **Réindexation incrémentale** : Optimiser les mises à jour
3. **Multi-index** : Un index par domaine/langue
4. **Métadonnées FAISS** : Filtrage par source/langue dans FAISS
5. **A/B Testing** : Comparer différents modèles d'embeddings
