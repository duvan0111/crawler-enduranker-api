# Workflow Global de Traitement - EduRanker API

## Vue d'ensemble

Le workflow global permet de traiter une requête utilisateur de bout en bout, depuis la collecte de ressources jusqu'au retour des 10 meilleures ressources éducatives.

## Architecture du Workflow

Le workflow se compose de 6 étapes principales :

### 1. Sauvegarde de la Question
- La question de l'utilisateur est sauvegardée dans MongoDB
- Génération automatique d'un embedding vectoriel (384 dimensions)
- Détection de la langue

### 2. Crawling des Sources
- Collecte de ressources depuis :
  - **Wikipedia** : Articles éducatifs (FR/EN)
  - **GitHub** : Repositories et README
  - **Medium** : Articles de blog
- Génération d'embeddings pour chaque ressource
- Sauvegarde dans MongoDB

### 3. Reconstruction de l'Index FAISS
- Reconstruction de l'index FAISS avec toutes les ressources
- Indexation des embeddings pour la recherche sémantique rapide
- Sauvegarde de l'index sur disque

### 4. Recherche Sémantique (FAISS)
- Recherche des ressources les plus pertinentes
- Utilisation de la similarité cosine
- Retour des top K résultats (par défaut 50)

### 5. Re-ranking avec Cross-Encoder
- Affinage du classement avec un modèle BERT cross-encoder
- Score de pertinence plus précis
- Réduction au top 10 final

### 6. Sauvegarde des Inférences
- Sauvegarde des résultats dans la collection `inference`
- Tracking des scores pour chaque ressource
- Utilisation pour le fine-tuning du modèle

## Endpoint API

### POST `/api/workflow/process`

Traite une requête complète et retourne le top 10 des meilleures ressources.

#### Requête

```json
{
  "question": "Comment apprendre le machine learning ?",
  "max_par_site": 15,
  "sources": ["wikipedia", "github", "medium"],
  "langues": ["fr", "en"],
  "top_k_faiss": 50,
  "top_k_final": 10
}
```

#### Paramètres

| Paramètre | Type | Défaut | Description |
|-----------|------|--------|-------------|
| `question` | string | **requis** | Question de l'utilisateur |
| `max_par_site` | int | 15 | Nombre max de résultats par site |
| `sources` | array | ["wikipedia", "github", "medium"] | Sources à crawler |
| `langues` | array | ["fr", "en"] | Langues pour Wikipedia |
| `top_k_faiss` | int | 50 | Nombre de résultats FAISS |
| `top_k_final` | int | 10 | Nombre de résultats finaux |

#### Réponse

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
      "url": "https://example.com/ml-intro",
      "auteur": "John Doe",
      "date": "2024-01-15",
      "score_faiss": 0.85,
      "score_reranking": 0.92,
      "score_final": 0.89,
      "mots_cles": ["machine learning", "IA", "éducation"],
      "source": "wikipedia",
      "id_inference": "507f1f77bcf86cd799439012"
    }
  ],
  "sources_crawlees": ["wikipedia", "github", "medium"],
  "erreurs": []
}
```

#### Format des Résultats

Chaque ressource dans `resultats` contient :

| Champ | Type | Description |
|-------|------|-------------|
| `titre` | string | Titre de la ressource |
| `url` | string | URL de la ressource |
| `auteur` | string | Auteur (si disponible) |
| `date` | string | Date de publication |
| `score_faiss` | float | Score de similarité FAISS (0-1) |
| `score_reranking` | float | Score du cross-encoder |
| `score_final` | float | Score combiné (0.3×FAISS + 0.7×reranking) |
| `mots_cles` | array | Mots-clés de la ressource |
| `source` | string | Source (wikipedia/github/medium) |
| `id_inference` | string | ID de l'inférence MongoDB |

## Exemples d'Utilisation

### Exemple 1 : Requête Simple

```bash
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Comment apprendre Python ?"
  }'
```

### Exemple 2 : Requête Personnalisée

```bash
curl -X POST "http://localhost:8000/api/workflow/process" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Deep learning for computer vision",
    "max_par_site": 20,
    "sources": ["github", "medium"],
    "langues": ["en"],
    "top_k_faiss": 100,
    "top_k_final": 15
  }'
```

### Exemple 3 : Avec Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/workflow/process",
    json={
        "question": "Comment utiliser TensorFlow ?",
        "max_par_site": 15,
        "sources": ["wikipedia", "github"],
        "langues": ["fr", "en"],
        "top_k_faiss": 50,
        "top_k_final": 10
    }
)

data = response.json()
print(f"Nombre de résultats : {data['total_resultats_final']}")

for i, ressource in enumerate(data['resultats'], 1):
    print(f"\n{i}. {ressource['titre']}")
    print(f"   URL: {ressource['url']}")
    print(f"   Score: {ressource['score_final']:.3f}")
    print(f"   Source: {ressource['source']}")
```

## Performances

### Temps d'Exécution Typiques

| Étape | Durée Moyenne |
|-------|---------------|
| Sauvegarde question | < 0.1s |
| Crawling | 10-30s |
| Reconstruction index | 1-5s |
| Recherche FAISS | 0.1-0.5s |
| Re-ranking | 1-3s |
| **Total** | **12-40s** |

### Optimisations

- **Cache** : Les ressources sont réutilisées entre les requêtes
- **Index FAISS** : Recherche ultra-rapide (même avec 100k+ ressources)
- **Parallélisation** : Crawling des sources en parallèle
- **Fine-tuning** : Le modèle s'améliore avec les feedbacks

## Flux de Données

```
Question Utilisateur
       ↓
[1] Sauvegarde + Embedding
       ↓
[2] Crawling Multi-Sources → MongoDB
       ↓
[3] Index FAISS ← Embeddings
       ↓
[4] Recherche FAISS → Top 50
       ↓
[5] Cross-Encoder → Top 10
       ↓
[6] Sauvegarde Inférences
       ↓
   Top 10 Résultats
```

## Gestion des Erreurs

Le workflow est robuste et continue même si certaines étapes échouent :

- **Erreur crawling** : Continue avec les sources disponibles
- **Erreur index FAISS** : Utilise l'index existant
- **Erreur re-ranking** : Retourne les résultats FAISS bruts
- **Toutes les erreurs** : Sont listées dans `erreurs[]`

## Monitoring

### Health Check

```bash
curl http://localhost:8000/api/workflow/health
```

### Logs

Les logs détaillés sont disponibles dans la console :

```
🚀 Début du workflow pour la question: Comment apprendre le ML ?
📝 ÉTAPE 1/6: Sauvegarde de la question utilisateur...
✅ Question sauvegardée (ID: 507f...)
🕷️  ÉTAPE 2/6: Lancement du crawling...
✅ Crawling terminé: 45 ressources en 12.50s
🔄 ÉTAPE 3/6: Reconstruction de l'index FAISS...
✅ Index FAISS reconstruit: 1234 vecteurs
🔍 ÉTAPE 4/6: Recherche sémantique avec FAISS...
✅ Recherche FAISS: 50 résultats en 0.30s
🎯 ÉTAPE 5/6: Re-ranking avec cross-encoder...
✅ Re-ranking terminé: 10 résultats en 1.20s
💾 ÉTAPE 6/6: Sauvegarde des inférences...
✅ Workflow terminé en 14.00s
📊 Résultats: 10 ressources finales
```

## Intégration Frontend

Le format de réponse est optimisé pour l'affichage frontend :

```javascript
// Affichage des résultats
response.resultats.forEach((ressource, index) => {
  console.log(`${index + 1}. ${ressource.titre}`);
  console.log(`   Score: ${ressource.score_final.toFixed(2)}`);
  console.log(`   Source: ${ressource.source}`);
  
  // Badge de qualité basé sur le score
  const badge = ressource.score_final > 0.8 ? '🏆' : 
                ressource.score_final > 0.6 ? '⭐' : '✓';
  console.log(`   ${badge} ${ressource.url}`);
});

// Statistiques
console.log(`\nStatistiques:`);
console.log(`- Ressources crawlées: ${response.total_crawle}`);
console.log(`- Temps total: ${response.duree_totale_secondes}s`);
console.log(`- Sources: ${response.sources_crawlees.join(', ')}`);
```

## Limites et Considérations

### Limites Techniques

- **Max résultats par site** : 50 (pour éviter le rate limiting)
- **Timeout** : 60s par source
- **Index FAISS** : Capacité illimitée (mais performance dégradée > 1M vecteurs)

### Considérations

- Le crawling peut être lent (10-30s) selon les sources
- Les résultats dépendent de la qualité des sources
- Le re-ranking nécessite un GPU pour de meilleures performances
- Les embeddings occupent ~1.5KB par ressource

## Prochaines Étapes

1. **Utiliser le workflow** : Testez avec différentes questions
2. **Collecter des feedbacks** : Utilisez `/api/reranking/feedback`
3. **Fine-tuner le modèle** : Exécutez le notebook de fine-tuning
4. **Améliorer les scores** : Le modèle s'améliore avec l'usage

## Support

Pour toute question ou problème :
- 📚 Documentation : `/docs`
- 🔍 API Docs : `http://localhost:8000/docs`
- 💡 Exemples : Voir les notebooks dans `/notebooks`
