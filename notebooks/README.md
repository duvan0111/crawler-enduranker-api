# 📓 Notebooks - Fine-Tuning et Analyse

Ce répertoire contient les Jupyter Notebooks pour le fine-tuning et l'analyse du système EduRanker.

## 📋 Notebooks Disponibles

### `fine_tune_cross_encoder.ipynb` ⭐

**Notebook principal pour fine-tuner le modèle cross-encoder.**

#### 🎯 Objectif
Fine-tuner le modèle cross-encoder sur les feedbacks utilisateurs collectés pour améliorer la qualité du reranking.

#### 📊 Contenu
1. **Configuration** : Connexion MongoDB, paramètres du modèle
2. **Chargement des données** : Récupération des feedbacks depuis MongoDB
3. **Préparation** : Création des paires d'entraînement (query, document, label)
4. **Visualisation** : Analyse exploratoire des données
5. **Fine-tuning** : Entraînement du modèle avec sentence-transformers
6. **Évaluation** : Métriques de performance (accuracy, F1, AUC)
7. **Comparaison** : Avant/après fine-tuning
8. **Sauvegarde** : Export du modèle et des métadonnées

#### 🚀 Utilisation

**1. Prérequis**
```bash
# Installer Jupyter
pip install jupyter notebook ipykernel

# Installer les dépendances
pip install sentence-transformers torch pymongo pandas matplotlib seaborn scikit-learn
```

**2. Lancer Jupyter**
```bash
cd notebooks
jupyter notebook
```

**3. Ouvrir le notebook**
- Ouvrir `fine_tune_cross_encoder.ipynb`
- Exécuter les cellules dans l'ordre (Shift+Enter)

**4. Configuration**
Modifier les variables si nécessaire :
```python
MONGODB_URL = "mongodb://localhost:27017"  # URL MongoDB
MONGODB_DB = "edu_ranker_db"                # Nom de la base
BASE_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Modèle de base
MODEL_OUTPUT_PATH = "models/cross_encoder_finetuned"      # Dossier de sortie
```

**5. Hyperparamètres**
Ajustables selon vos besoins :
```python
NUM_EPOCHS = 3          # Nombre d'époques (1-10)
BATCH_SIZE = 16         # Taille des batchs (4-64)
LEARNING_RATE = 2e-5    # Taux d'apprentissage
```

#### 📦 Sorties Générées

Après exécution, le notebook génère :
```
models/cross_encoder_finetuned/
├── config.json                    # Configuration du modèle
├── pytorch_model.bin              # Poids du modèle fine-tuné
├── training_metadata.pkl          # Métadonnées d'entraînement
└── training_report.txt            # Rapport détaillé
```

#### 📈 Métriques Évaluées

- **Accuracy** : Précision globale
- **Precision** : Précision des prédictions positives
- **Recall** : Rappel (sensibilité)
- **F1-Score** : Moyenne harmonique de precision/recall
- **AUC-ROC** : Aire sous la courbe ROC

#### ⚙️ Fonctionnement

```
┌─────────────────────────────────────────────────────────────┐
│                    PIPELINE DE FINE-TUNING                   │
└─────────────────────────────────────────────────────────────┘

1. CHARGEMENT DES DONNÉES
   ├─ Connexion MongoDB
   ├─ Récupération inférences avec feedback
   └─ Jointure avec user_queries et resources

2. PRÉPARATION
   ├─ Extraction (query_text, document_text, label)
   ├─ Label : 1.0 (like) ou 0.0 (dislike)
   └─ Split train/val (80/20)

3. FINE-TUNING
   ├─ Chargement modèle de base
   ├─ Configuration optimiseur (Adam)
   ├─ Entraînement (3 epochs par défaut)
   └─ Sauvegarde automatique

4. ÉVALUATION
   ├─ Prédictions sur validation
   ├─ Calcul des métriques
   └─ Comparaison avant/après

5. SAUVEGARDE
   ├─ Modèle fine-tuné
   ├─ Métadonnées
   └─ Rapport d'entraînement
```

#### 🎯 Prérequis de Données

**Minimum recommandé** :
- ✅ Au moins **50 feedbacks** (like/dislike)
- ✅ Distribution équilibrée (50% like, 50% dislike)
- ✅ Feedbacks de qualité (vrais utilisateurs)

**Pour de meilleures performances** :
- 🌟 **100-500 feedbacks** : Bon
- 🌟 **500-1000 feedbacks** : Très bon
- 🌟 **>1000 feedbacks** : Excellent

#### 📊 Visualisations

Le notebook génère plusieurs graphiques :
1. **Distribution des labels** : Répartition like/dislike
2. **Longueur des requêtes** : Histogramme
3. **Comparaison des performances** : Avant/après
4. **Distribution des scores** : Prédictions du modèle
5. **Matrice de confusion** : Analyse des erreurs

#### ⚠️ Notes Importantes

1. **GPU recommandé** : Le fine-tuning est plus rapide sur GPU (CUDA)
   - CPU : ~5-15 minutes pour 100 exemples
   - GPU : ~1-3 minutes pour 100 exemples

2. **Mémoire** :
   - RAM : Minimum 4GB
   - GPU : Minimum 2GB VRAM

3. **Durée** :
   - Dépend du nombre d'exemples et d'epochs
   - ~1 minute par epoch pour 100 exemples (GPU)

4. **Réentraînement** :
   - Relancer le notebook périodiquement
   - Recommandé après 100+ nouveaux feedbacks

#### 🔧 Dépannage

**Erreur : "Pas assez de feedbacks"**
- Collecter plus de feedbacks via l'API
- Minimum : 10 feedbacks (test), 50+ (recommandé)

**Erreur : "CUDA out of memory"**
- Réduire `BATCH_SIZE` (ex: 8 ou 4)
- Utiliser CPU : `device = "cpu"`

**Erreur : "Module not found"**
```bash
pip install sentence-transformers torch pymongo pandas matplotlib seaborn scikit-learn
```

**Modèle pas chargé dans l'API**
- Vérifier que le dossier existe : `models/cross_encoder_finetuned/`
- Vérifier les logs au démarrage de l'API
- Chemin configuré dans `.env` : `CROSS_ENCODER_PATH=models/cross_encoder_finetuned`

#### 🚀 Intégration avec l'API

Après le fine-tuning, le modèle est automatiquement utilisé par l'API :

1. **Redémarrer l'API** :
```bash
python main.py
```

2. **Vérifier le chargement** :
```bash
curl http://localhost:8000/api/reranking/info-modele
```

3. **Tester** :
```bash
curl -X POST "http://localhost:8000/api/reranking/search-with-reranking" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "machine learning tutorial", "use_reranker": true}'
```

#### 📈 Workflow Recommandé

```
1. Collecter des feedbacks
   └─> Utiliser l'API en production
   └─> Objectif : 100+ feedbacks

2. Fine-tuner le modèle
   └─> Exécuter ce notebook
   └─> Vérifier les métriques

3. Déployer
   └─> Redémarrer l'API
   └─> Tester les performances

4. Monitorer
   └─> Suivre les nouvelles métriques
   └─> Collecter plus de feedbacks

5. Répéter (cycle d'amélioration continue)
   └─> Réentraîner tous les mois
   └─> Ou après 100+ nouveaux feedbacks
```

#### 📚 Ressources

- **Sentence-Transformers** : https://www.sbert.net/
- **Cross-Encoder** : https://www.sbert.net/examples/applications/cross-encoder/README.html
- **Documentation API** : http://localhost:8000/docs

---

## 🎯 Prochains Notebooks (À venir)

- `analyze_performance.ipynb` : Analyse des performances du système
- `data_exploration.ipynb` : Exploration des données collectées
- `ab_testing.ipynb` : Comparaison de différents modèles
- `user_behavior.ipynb` : Analyse du comportement utilisateur

---

## 📞 Support

Pour toute question ou problème :
1. Vérifier la documentation : `docs/INFERENCE_TRACKING.md`
2. Consulter les logs de l'API
3. Tester avec des exemples simples

---

**Créé le** : 8 décembre 2024  
**Version** : 1.0  
**Auteur** : EduRanker Development Team
