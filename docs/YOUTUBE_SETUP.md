# 🎥 Configuration YouTube API - Guide Rapide

## Étape 1: Obtenir une clé API (5 minutes)

### 1.1 Créer un compte Google Cloud (gratuit)

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Se connecter avec votre compte Google
3. Accepter les conditions d'utilisation

### 1.2 Créer un projet

1. Cliquer sur le menu déroulant du projet (en haut)
2. Cliquer sur "NEW PROJECT"
3. Nom du projet: `eduranker-youtube` (ou autre nom)
4. Cliquer sur "CREATE"
5. Attendre quelques secondes que le projet soit créé

### 1.3 Activer YouTube Data API v3

1. Dans le menu navigation (☰), aller à:
   - **APIs & Services** → **Library**
2. Dans la barre de recherche, taper: `YouTube Data API v3`
3. Cliquer sur **YouTube Data API v3**
4. Cliquer sur le bouton **ENABLE**
5. Attendre l'activation (quelques secondes)

### 1.4 Créer une clé API

1. Aller dans: **APIs & Services** → **Credentials**
2. Cliquer sur **+ CREATE CREDENTIALS** (en haut)
3. Sélectionner **API key**
4. Une popup apparaît avec votre clé API
5. **COPIER** la clé (elle ressemble à: `AIzaSyD...xyz123`)
6. (Optionnel) Cliquer sur **RESTRICT KEY** pour sécuriser:
   - Application restrictions: **None** (pour les tests)
   - API restrictions: Sélectionner **YouTube Data API v3**
   - Cliquer **SAVE**

## Étape 2: Configurer EduRanker

### 2.1 Créer le fichier .env

Si vous n'avez pas encore de fichier `.env`, copiez `.env.example`:

```bash
cp .env.example .env
```

### 2.2 Ajouter la clé API

Ouvrir le fichier `.env` et ajouter:

```bash
YOUTUBE_API_KEY=AIzaSyD...votre_cle_complete_ici
```

**⚠️ Important**: 
- Ne partagez jamais votre clé API publiquement
- Ne commitez pas le fichier `.env` sur Git
- Utilisez `.gitignore` pour exclure `.env`

## Étape 3: Tester l'intégration

### 3.1 Installer les dépendances (si nécessaire)

```bash
pip install -r requirements.txt
```

### 3.2 Lancer le script de test

```bash
python test_youtube_integration.py
```

### 3.3 Résultat attendu

```
======================================================================
🎥 Test d'intégration YouTube Data API v3
======================================================================

✅ Clé API trouvée: AIzaSyD...xyz123
📦 MongoDB: mongodb://localhost:27017 / eduranker_db
✅ Service crawler initialisé

======================================================================
TEST 1: Collecte YouTube uniquement
======================================================================

🔍 Question: Python machine learning tutorial
📊 Max par site: 5

✅ Collecte terminée en 3.45s
📹 Vidéos collectées: 10

  youtube: 10 ressources (statut: succès)

📝 Exemples de vidéos collectées:

1. Machine Learning Tutorial for Beginners
   URL: https://www.youtube.com/watch?v=...
   Auteur: freeCodeCamp.org
   Langue: en
   Popularité: 2,500,000
   Embedding: 384 dimensions
...
```

## Étape 4: Utiliser via l'API REST

### 4.1 Démarrer le serveur

```bash
python main.py
```

### 4.2 Test avec curl

```bash
curl -X POST "http://localhost:8000/api/crawler/collecter" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Python pandas tutorial",
    "max_par_site": 5,
    "sources": ["youtube"]
  }'
```

### 4.3 Test avec l'interface Swagger

1. Ouvrir: http://localhost:8000/docs
2. Aller à **POST /api/crawler/collecter**
3. Cliquer sur "Try it out"
4. Modifier le JSON:
   ```json
   {
     "question": "machine learning",
     "max_par_site": 5,
     "sources": ["youtube"]
   }
   ```
5. Cliquer sur "Execute"

## Gestion des Quotas

### Comprendre les quotas

- **Quota gratuit**: 10,000 unités/jour
- **Recherche vidéo**: ~100 unités
- **Détails vidéo**: ~1 unité par vidéo

### Calcul pour vos tests

| Action | Unités | Nombre/jour |
|--------|--------|-------------|
| Recherche 5 vidéos | ~105 | ~95 fois |
| Recherche 10 vidéos | ~110 | ~90 fois |
| Workflow complet (10 vidéos) | ~110 | ~90 fois |

### Surveiller votre quota

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. **APIs & Services** → **Dashboard**
3. Cliquer sur **YouTube Data API v3**
4. Voir les **Quotas** et l'utilisation en temps réel

### Si vous dépassez le quota

**Message d'erreur**:
```json
{
  "error": {
    "code": 403,
    "message": "The request cannot be completed because you have exceeded your quota."
  }
}
```

**Solutions**:
- Attendre le lendemain (reset à minuit PST)
- Demander une augmentation de quota (gratuit, sous approbation)
- Réduire `max_par_site` dans vos requêtes

## Dépannage

### Erreur: "API key not valid"

**Cause**: Clé API incorrecte ou mal configurée

**Solutions**:
1. Vérifier que la clé est correcte dans `.env`
2. Vérifier que YouTube Data API v3 est activée
3. Vérifier les restrictions de clé (si configurées)
4. Regénérer une nouvelle clé API

### Erreur: "YOUTUBE_API_KEY non configurée"

**Cause**: Variable d'environnement non chargée

**Solutions**:
1. Vérifier que le fichier `.env` existe
2. Vérifier que `YOUTUBE_API_KEY` est bien défini
3. Redémarrer le serveur après modification du `.env`
4. Vérifier que `python-dotenv` est installé

### Erreur: "403 Forbidden"

**Cause**: API désactivée ou quota dépassé

**Solutions**:
1. Vérifier que YouTube Data API v3 est activée
2. Vérifier le quota sur Google Cloud Console
3. Attendre 24h si quota dépassé

### Aucune vidéo collectée

**Causes possibles**:
- Question trop spécifique
- Aucun résultat pour la langue demandée
- Erreur réseau

**Solutions**:
1. Tester avec une question plus générique: "python tutorial"
2. Vérifier les logs du serveur
3. Essayer avec `langues=['en']` uniquement

## Optimisations

### 1. Limiter les résultats

Pour économiser votre quota:

```python
resultats = await crawler_service.collecter_ressources(
    question="python",
    max_par_site=3,  # Au lieu de 10
    sources=['youtube']
)
```

### 2. Cache des résultats

Les résultats sont automatiquement sauvegardés dans MongoDB. 
La prochaine recherche identique ne consommera pas de quota.

### 3. Cibler une langue

```python
resultats = await crawler_service.collecter_ressources(
    question="python",
    max_par_site=5,
    sources=['youtube'],
    langues=['en']  # Seulement anglais
)
```

## Ressources supplémentaires

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [API Explorer](https://developers.google.com/youtube/v3/docs)
- [Support Forum](https://support.google.com/youtube/community)

## Support

Si vous rencontrez des problèmes:

1. Vérifier les logs: `tail -f logs/app.log`
2. Tester la clé API avec l'API Explorer
3. Consulter le quota sur Google Cloud Console
4. Lire la documentation officielle

---

**Bon crawling! 🎥📚**
