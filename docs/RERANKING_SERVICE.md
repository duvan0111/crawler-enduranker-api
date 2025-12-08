# Service de Re-ranking avec Cross-Encoder - Documentation

## 🎯 Vue d'ensemble

Le service de re-ranking utilise un **cross-encoder BERT** pour affiner le classement des résultats obtenus via FAISS. Contrairement aux bi-encoders (utilisés dans FAISS), le cross-encoder traite simultanément la requête et le document, offrant une précision supérieure au prix d'une vitesse réduite.

## 🏗️ Architecture

### Pipeline de recherche complet

```
┌─────────────────┐
│ Requête user    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  1. RECHERCHE FAISS             │
│     (Bi-encoder)                │
│                                 │
│  • Rapide (< 1ms)               │
│  • Recall élevé                 │
│  • Top-K candidats (50-100)     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  2. RE-RANKING                  │
│     (Cross-encoder)             │
│                                 │
│  • Plus lent (~10-50ms)         │
│  • Précision élevée             │
│  • Score de pertinence fin      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  3. RÉSULTATS FINAUX            │
│                                 │
│  • Top-10 meilleurs résultats   │
│  • Classement optimal           │
└─────────────────────────────────┘
```

### Différence Bi-encoder vs Cross-encoder

| Aspect | Bi-encoder (FAISS) | Cross-encoder (Re-ranking) |
|--------|-------------------|---------------------------|
| **Architecture** | Encode query et docs séparément | Encode query+doc ensemble |
| **Vitesse** | Très rapide (< 1ms) | Plus lent (10-50ms) |
| **Précision** | Bonne | Excellente |
| **Usage** | Première étape (recall) | Seconde étape (precision) |
| **Scalabilité** | Millions de docs | Centaines de docs |

## 🧠 Modèle Cross-Encoder

### Modèle de base

**Nom**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

- Pré-entraîné sur MS MARCO (Microsoft Machine Reading Comprehension)
- 22.7M de paramètres
- Optimisé pour la recherche de passage
- Support multilingue limité (principalement EN)

### Fonctionnement

```python
# Input: Paire (query, document)
input_text = "[CLS] query [SEP] document [SEP]"

# BERT processing
hidden_states = bert_model(input_text)

# Classification head
relevance_score = classifier(hidden_states[CLS])

# Output: Score de pertinence (-∞, +∞)
# Typiquement entre -5 et +5
```

## 💾 Données d'entraînement

### Collecte des feedbacks

Les feedbacks utilisateurs sont sauvegardés dans MongoDB :

```javascript
{
  _id: ObjectId("..."),
  user_query_id: "507f1f77bcf86cd799439011",
  resource_id: "507f1f77bcf86cd799439012",
  query_text: "machine learning tutorial",
  resource_title: "Introduction to ML",
  resource_text: "Machine learning is...",
  feedback_type: "like",  // like, dislike, click, view
  relevance_score: 1.0,   // 1.0 = pertinent, 0.0 = non pertinent
  session_id: "session_123",
  date_feedback: ISODate("2024-01-20T10:30:00Z")
}
```

### Types de feedback

| Type | Label | Utilisation |
|------|-------|-------------|
| `like` | 1.0 | Ressource pertinente (feedback explicite) |
| `dislike` | 0.0 | Ressource non pertinente (feedback explicite) |
| `click` | 0.75 | Click sur la ressource (feedback implicite) |
| `view` | 0.5 | Vue de la ressource (feedback faible) |

## 🎓 Fine-tuning

### Prérequis

- **Minimum**: 10 feedbacks (like/dislike)
- **Recommandé**: 100+ feedbacks pour de bons résultats
- **Optimal**: 1000+ feedbacks

### Processus de fine-tuning

```python
# 1. Récupération des feedbacks depuis MongoDB
feedbacks = await reranking_service.recuperer_donnees_entrainement()

# 2. Création des paires d'entraînement
training_pairs = [
    {
        "texts": [query, document],
        "label": relevance_score  # 0.0 à 1.0
    }
    for feedback in feedbacks
]

# 3. Fine-tuning
model.fit(
    train_dataloader=train_dataloader,
    epochs=3,
    warmup_steps=warmup_steps,
    output_path="models/cross_encoder"
)

# 4. Sauvegarde automatique
# - models/cross_encoder/config.json
# - models/cross_encoder/pytorch_model.bin
# - models/cross_encoder/metadata.pkl
```

### Hyperparamètres

| Paramètre | Valeur par défaut | Description |
|-----------|-------------------|-------------|
| `num_epochs` | 3 | Nombre d'époques |
| `batch_size` | 16 | Taille des batchs |
| `learning_rate` | 2e-5 | Taux d'apprentissage |
| `warmup_steps` | 10% du total | Montée progressive du LR |

## 📡 API Endpoints

### 1. Recherche avec re-ranking

```http
POST /api/reranking/recherche-avec-reranking
Content-Type: application/json

{
  "question": "machine learning tutorial",
  "top_k_faiss": 50,
  "top_k_final": 10,
  "use_reranker": true
}
```

**Réponse**:
```json
{
  "question": "machine learning tutorial",
  "nb_resultats_faiss": 50,
  "nb_resultats_finaux": 10,
  "reranking_applique": true,
  "resultats": [
    {
      "resource_id": "507f...",
      "titre": "Introduction to Machine Learning",
      "url": "https://...",
      "source": "wikipedia",
      "faiss_score": 0.85,
      "reranking_score": 3.42,
      "final_score": 0.89,
      "rank": 1
    }
  ],
  "duree_recherche_ms": 125.5
}
```

### 2. Soumettre un feedback

```http
POST /api/reranking/feedback
Content-Type: application/json

{
  "query_id": "507f1f77bcf86cd799439011",
  "resource_id": "507f1f77bcf86cd799439012",
  "feedback_type": "like",
  "session_id": "session_123"
}
```

### 3. Statistiques des feedbacks

```http
GET /api/reranking/statistiques-feedback
```

**Réponse**:
```json
{
  "nb_feedbacks_total": 150,
  "nb_likes": 100,
  "nb_dislikes": 50,
  "nb_training_pairs": 150,
  "model_version": "finetuned_20240120_143000",
  "last_training_date": "2024-01-20T14:30:00"
}
```

### 4. Lancer le fine-tuning

```http
POST /api/reranking/fine-tune?num_epochs=3&batch_size=16&learning_rate=2e-5
```

⚠️ **Attention**: Cette opération peut prendre plusieurs minutes selon le nombre de données.

### 5. Prédire un score de pertinence

```http
POST /api/reranking/predict-score?query=machine%20learning&document=Introduction%20to%20ML...
```

**Réponse**:
```json
{
  "status": "success",
  "query": "machine learning",
  "document": "Introduction to ML...",
  "raw_score": 3.42,
  "normalized_score": 0.91,
  "interpretation": "Très pertinent"
}
```

### 6. Informations sur le modèle

```http
GET /api/reranking/info-modele
```

## 🔄 Workflow recommandé

### Phase 1: Démarrage (Modèle de base)

```
1. Démarrer l'application
   → Modèle de base chargé automatiquement

2. Utiliser le re-ranking avec le modèle de base
   → Bons résultats génériques

3. Collecter des feedbacks utilisateurs
   → Like/Dislike sur les résultats
```

### Phase 2: Collecte de données

```
4. Les utilisateurs interagissent avec le système
   → Feedbacks sauvegardés automatiquement

5. Monitorer les statistiques
   GET /api/reranking/statistiques-feedback

6. Attendre d'avoir suffisamment de données
   → Minimum 10, recommandé 100+
```

### Phase 3: Fine-tuning

```
7. Lancer le fine-tuning
   POST /api/reranking/fine-tune

8. Le modèle s'adapte à vos données
   → 3-10 minutes selon la quantité de données

9. Modèle fine-tuné sauvegardé automatiquement
   → models/cross_encoder/

10. Rechargement automatique du modèle fine-tuné
    → Meilleurs résultats pour votre domaine
```

### Phase 4: Amélioration continue

```
11. Continuer à collecter des feedbacks

12. Re-fine-tuner périodiquement
    → Tous les X nouveaux feedbacks
    → Tous les X jours/semaines

13. Le modèle s'améliore progressivement
    → Adaptation continue à vos utilisateurs
```

## 📊 Scoring

### Score FAISS (similarité cosine)

- **Range**: 0 à 1
- **Calcul**: Produit scalaire des embeddings normalisés
- **Interprétation**: Similarité sémantique générale

### Score Re-ranking (cross-encoder)

- **Range**: -∞ à +∞ (typiquement -5 à +5)
- **Calcul**: Output du classificateur BERT
- **Normalisation**: Sigmoïde pour ramener à [0, 1]

```python
score_normalized = 1 / (1 + exp(-raw_score))
```

### Score final combiné

```python
final_score = α × faiss_score + (1 - α) × reranking_score_normalized
```

- **α** (alpha): Poids pour FAISS (par défaut: 0.3)
- **(1 - α)**: Poids pour re-ranking (par défaut: 0.7)

**Justification**: Le cross-encoder est plus précis, on lui donne plus de poids.

## 🎯 Cas d'usage

### 1. Amélioration de la précision

**Problème**: FAISS retourne des résultats similaires mais pas toujours pertinents.

**Solution**: Le cross-encoder affine en analysant la pertinence réelle.

### 2. Adaptation au domaine

**Problème**: Modèle générique pas optimal pour votre domaine spécifique.

**Solution**: Fine-tuning sur vos feedbacks utilisateurs.

### 3. Personnalisation

**Problème**: Différents utilisateurs ont des préférences différentes.

**Solution**: Feedbacks par session/utilisateur → modèle personnalisé.

## ⚡ Performance

### Temps de réponse

| Étape | Temps typique |
|-------|---------------|
| FAISS (50 candidats) | 1-5 ms |
| Cross-encoder (50 docs) | 50-200 ms |
| **Total** | **50-200 ms** |

### Optimisations possibles

1. **Réduire les candidats**: 50 au lieu de 100
2. **Batch processing**: Traiter plusieurs requêtes ensemble
3. **GPU**: Utiliser un GPU pour le cross-encoder
4. **Caching**: Mettre en cache les scores fréquents
5. **Modèle plus léger**: Utiliser MiniLM-L-2 au lieu de L-6

## 🐛 Dépannage

### Le fine-tuning échoue

**Symptôme**: Erreur "Pas assez de données"

**Solution**: Collectez plus de feedbacks (minimum 10)

### Modèle ne s'améliore pas

**Symptôme**: Pas de différence avant/après fine-tuning

**Causes possibles**:
- Pas assez de données (< 100)
- Données de mauvaise qualité
- Feedbacks trop uniformes (tous likes ou tous dislikes)

**Solutions**:
- Collecter plus de feedbacks diversifiés
- Vérifier la qualité des feedbacks
- Augmenter le nombre d'époques

### Re-ranking trop lent

**Symptôme**: Temps de réponse > 500ms

**Solutions**:
- Réduire `top_k_faiss` (ex: 30 au lieu de 50)
- Utiliser un GPU
- Désactiver temporairement le re-ranking pour certaines requêtes

## 📈 Métriques de qualité

### Avant/après fine-tuning

À mesurer :
- **Precision@5**: Proportion de résultats pertinents dans le top 5
- **NDCG@10**: Normalized Discounted Cumulative Gain
- **Click-through rate**: Taux de clics sur les résultats
- **User satisfaction**: Ratio likes/(likes+dislikes)

## 🔮 Évolutions futures

1. **Modèles multilingues**: Utiliser un cross-encoder FR/EN
2. **Contextualisation**: Prendre en compte l'historique utilisateur
3. **A/B Testing**: Comparer différents modèles
4. **Apprentissage continu**: Re-training automatique
5. **Ensemble methods**: Combiner plusieurs cross-encoders

## 📖 Références

- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [MS MARCO Dataset](https://microsoft.github.io/msmarco/)
- [Cross-Encoders for Semantic Search](https://www.sbert.net/examples/applications/cross-encoder/README.html)
- [BERT Paper](https://arxiv.org/abs/1810.04805)

## 🎓 Concepts clés

### Cross-Encoder vs Bi-Encoder

**Bi-Encoder** (FAISS):
```
Query    → Encoder₁ → Embedding₁ ─┐
                                   ├─ Similarité
Document → Encoder₂ → Embedding₂ ─┘
```

**Cross-Encoder** (Re-ranking):
```
[Query + Document] → BERT → Classificateur → Score
```

### Transfer Learning

1. **Pré-entraînement**: Modèle entraîné sur MS MARCO (millions d'exemples)
2. **Fine-tuning**: Adaptation sur vos données (centaines/milliers d'exemples)
3. **Avantage**: Peu de données nécessaires grâce au pré-entraînement

---

**Date de création**: 2024-01-20  
**Version**: 1.0.0  
**Statut**: ✅ Production Ready
