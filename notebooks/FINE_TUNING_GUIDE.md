# 📓 Fine-Tuning via Jupyter Notebook - Guide Complet

## 🎯 Vue d'Ensemble

Le **fine-tuning du cross-encoder** se fait désormais via un **Jupyter Notebook interactif** plutôt que via l'API. Cette approche offre de nombreux avantages :

✅ **Visualisations détaillées** : Graphiques et analyses en temps réel  
✅ **Contrôle total** : Accès à tous les paramètres et métriques  
✅ **Reproductibilité** : Sauvegarde automatique des configurations  
✅ **Debugging facile** : Inspection des données à chaque étape  
✅ **Rapport automatique** : Génération d'un rapport d'entraînement complet  

---

## 📂 Structure

```
notebooks/
├── README.md                           # Documentation complète
├── fine_tune_cross_encoder.ipynb       # Notebook principal ⭐
└── (futurs notebooks d'analyse)
```

---

## 🚀 Démarrage Rapide (5 minutes)

### 1. Installation

```bash
# Installer Jupyter et les dépendances
pip install jupyter notebook ipykernel
pip install sentence-transformers torch pymongo pandas matplotlib seaborn scikit-learn
```

### 2. Lancement

```bash
# Se placer dans le répertoire notebooks
cd notebooks

# Lancer Jupyter
jupyter notebook
```

Cela ouvrira votre navigateur avec l'interface Jupyter.

### 3. Exécution

1. Cliquer sur `fine_tune_cross_encoder.ipynb`
2. **Exécuter toutes les cellules** : Menu → Cell → Run All
3. Attendre la fin de l'entraînement (~5-15 minutes)
4. Consulter les métriques et visualisations

### 4. Résultat

Le notebook génère :
```
models/cross_encoder_finetuned/
├── config.json                    # Configuration
├── pytorch_model.bin              # Modèle fine-tuné
├── training_metadata.pkl          # Métadonnées
└── training_report.txt            # Rapport détaillé
```

### 5. Utilisation

```bash
# Redémarrer l'API (elle chargera automatiquement le modèle fine-tuné)
python main.py

# Tester
curl -X POST "http://localhost:8000/api/reranking/search-with-reranking" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "machine learning tutorial", "use_reranker": true}'
```

---

## 📊 Contenu du Notebook

### Section 1 : Configuration
- Imports et vérifications
- Connexion MongoDB
- Configuration des chemins

### Section 2 : Chargement des Données
- Statistiques des inférences
- Distribution des feedbacks
- Vérification de la qualité

### Section 3 : Préparation
- Extraction des paires (query, document, label)
- Création du DataFrame
- Statistiques descriptives

### Section 4 : Visualisation
- Distribution des labels (like/dislike)
- Longueur des requêtes
- Analyse exploratoire

### Section 5 : DataLoaders
- Split train/validation (80/20)
- Création des InputExamples
- Configuration des batchs

### Section 6 : Modèle de Base
- Chargement du cross-encoder
- Vérification GPU/CPU
- Comptage des paramètres

### Section 7 : Configuration
- Hyperparamètres (epochs, batch_size, learning_rate)
- Calcul des warmup steps
- Affichage du plan d'entraînement

### Section 8 : Évaluation Baseline
- Prédictions avant fine-tuning
- Calcul des métriques (accuracy, F1, AUC)
- Baseline pour comparaison

### Section 9 : Fine-Tuning 🚀
- Entraînement du modèle
- Barre de progression
- Sauvegarde automatique

### Section 10 : Évaluation Finale
- Rechargement du modèle fine-tuné
- Nouvelles prédictions
- Calcul des métriques améliorées

### Section 11 : Comparaison
- Tableau avant/après
- Calcul des améliorations
- Pourcentages de gain

### Section 12 : Visualisations
- Graphiques de comparaison
- Distribution des scores
- Matrice de confusion

### Section 13 : Tests
- Exemples de prédictions
- Interprétation des scores
- Validation qualitative

### Section 14 : Sauvegarde
- Export des métadonnées
- Génération du rapport
- Résumé final

---

## 🎛️ Configuration

### Variables Principales

```python
# MongoDB
MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB = "edu_ranker_db"

# Modèle
BASE_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MODEL_OUTPUT_PATH = "models/cross_encoder_finetuned"

# Hyperparamètres
NUM_EPOCHS = 3          # Nombre d'époques (1-10)
BATCH_SIZE = 16         # Taille des batchs (4-64)
LEARNING_RATE = 2e-5    # Taux d'apprentissage
```

### Ajustement des Hyperparamètres

| Paramètre | Par défaut | Recommandation | Impact |
|-----------|-----------|----------------|--------|
| `NUM_EPOCHS` | 3 | 2-5 | ↑ = Meilleur apprentissage mais ↑ temps |
| `BATCH_SIZE` | 16 | 8-32 | ↑ = Plus rapide mais ↑ mémoire |
| `LEARNING_RATE` | 2e-5 | 1e-5 à 5e-5 | ↑ = Apprentissage plus rapide mais instable |

**Conseils** :
- **Peu de données (<100)** : Réduire epochs (2-3), augmenter learning_rate (5e-5)
- **Beaucoup de données (>500)** : Augmenter epochs (5-7), garder learning_rate faible (2e-5)
- **Mémoire limitée** : Réduire batch_size (8 ou 4)
- **GPU puissant** : Augmenter batch_size (32 ou 64)

---

## 📈 Métriques Évaluées

### Accuracy (Précision globale)
- **Définition** : Proportion de prédictions correctes
- **Formule** : (TP + TN) / (TP + TN + FP + FN)
- **Interprétation** : 0.8 = 80% de prédictions correctes

### Precision (Précision positive)
- **Définition** : Proportion de vrais positifs parmi les prédictions positives
- **Formule** : TP / (TP + FP)
- **Interprétation** : 0.85 = 85% des "like" prédits sont corrects

### Recall (Rappel/Sensibilité)
- **Définition** : Proportion de vrais positifs détectés
- **Formule** : TP / (TP + FN)
- **Interprétation** : 0.90 = 90% des vrais "like" sont détectés

### F1-Score
- **Définition** : Moyenne harmonique de precision et recall
- **Formule** : 2 * (precision * recall) / (precision + recall)
- **Interprétation** : Équilibre entre precision et recall

### AUC-ROC
- **Définition** : Aire sous la courbe ROC
- **Interprétation** : 0.5 = hasard, 1.0 = parfait

---

## 🎯 Prérequis de Données

### Minimum Absolu
- ✅ **10 feedbacks** : Pour tester le notebook
- ⚠️ Performances limitées avec si peu de données

### Minimum Recommandé
- ✅ **50-100 feedbacks** : Pour un premier fine-tuning valide
- ✅ Distribution équilibrée (50% like, 50% dislike)

### Optimal
- 🌟 **200-500 feedbacks** : Bonnes performances
- 🌟 **>500 feedbacks** : Excellentes performances
- 🌟 **>1000 feedbacks** : Performances maximales

### Qualité des Données
- ✅ Feedbacks de **vrais utilisateurs** (pas de tests)
- ✅ Variété de requêtes et de ressources
- ✅ Distribution équilibrée des labels

---

## ⚡ Performances

### Temps d'Exécution

| Configuration | 100 exemples | 500 exemples | 1000 exemples |
|--------------|-------------|-------------|---------------|
| **CPU (4 cores)** | 5-8 min | 20-30 min | 40-60 min |
| **GPU (GTX 1060)** | 1-2 min | 5-8 min | 10-15 min |
| **GPU (RTX 3080)** | 30-60 sec | 2-3 min | 4-6 min |

### Mémoire Requise

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| **RAM** | 4 GB | 8 GB |
| **GPU VRAM** | - | 2-4 GB |
| **Disque** | 500 MB | 2 GB |

---

## 🐛 Dépannage

### Erreur : "Pas assez de feedbacks"

**Cause** : Moins de 10 feedbacks dans la base

**Solution** :
1. Collecter plus de feedbacks via l'API
2. Utiliser l'endpoint de test pour générer des feedbacks

```bash
# Générer des feedbacks de test
python scripts/test_inference_flow.py
```

### Erreur : "CUDA out of memory"

**Cause** : GPU mémoire insuffisante

**Solution** :
```python
# Dans le notebook, réduire la taille des batchs
BATCH_SIZE = 8  # ou 4

# OU forcer l'utilisation du CPU
device = "cpu"
```

### Erreur : "Module not found"

**Cause** : Dépendances manquantes

**Solution** :
```bash
pip install sentence-transformers torch pymongo pandas matplotlib seaborn scikit-learn
```

### Le modèle n'est pas chargé par l'API

**Vérifications** :
1. Le dossier existe : `models/cross_encoder_finetuned/`
2. Il contient `config.json` et `pytorch_model.bin`
3. Les logs de l'API au démarrage

**Solution** :
```bash
# Vérifier le chemin dans .env
CROSS_ENCODER_PATH=models/cross_encoder_finetuned

# Redémarrer l'API
python main.py

# Vérifier le chargement
curl http://localhost:8000/api/reranking/info-modele
```

---

## 📊 Workflow Complet

```
┌──────────────────────────────────────────────────────────────┐
│                   WORKFLOW DE FINE-TUNING                     │
└──────────────────────────────────────────────────────────────┘

1. COLLECTE DES DONNÉES
   ├─ Utiliser l'API en production
   ├─ Collecter feedbacks utilisateurs (like/dislike)
   └─ Objectif : 100+ feedbacks

2. PRÉPARATION
   ├─ Vérifier MongoDB : db.inference.count()
   ├─ Vérifier distribution des feedbacks
   └─ S'assurer d'avoir assez de données

3. FINE-TUNING
   ├─ Lancer Jupyter : jupyter notebook
   ├─ Ouvrir : fine_tune_cross_encoder.ipynb
   ├─ Configurer les hyperparamètres (si nécessaire)
   └─ Exécuter toutes les cellules

4. ÉVALUATION
   ├─ Consulter les métriques
   ├─ Vérifier l'amélioration vs baseline
   └─ Analyser les visualisations

5. VALIDATION
   ├─ Tester sur nouveaux exemples
   ├─ Vérifier la matrice de confusion
   └─ S'assurer que les performances sont satisfaisantes

6. DÉPLOIEMENT
   ├─ Redémarrer l'API : python main.py
   ├─ Vérifier le chargement du modèle
   └─ Tester via l'API

7. MONITORING
   ├─ Suivre les nouvelles métriques
   ├─ Collecter plus de feedbacks
   └─ Planifier le prochain réentraînement

8. CYCLE D'AMÉLIORATION CONTINUE
   └─ Répéter tous les 1-3 mois ou après 100+ nouveaux feedbacks
```

---

## 🔗 API vs Notebook

### Ancienne Méthode (API) ❌

```bash
curl -X POST "http://localhost:8000/api/reranking/fine-tune?num_epochs=3"
```

**Limitations** :
- ❌ Pas de visualisations
- ❌ Métriques limitées
- ❌ Pas de rapport détaillé
- ❌ Difficile à debugger
- ❌ Pas de contrôle intermédiaire

### Nouvelle Méthode (Notebook) ✅

```bash
cd notebooks
jupyter notebook
# Ouvrir fine_tune_cross_encoder.ipynb
```

**Avantages** :
- ✅ Visualisations riches (graphiques, distributions)
- ✅ Métriques complètes (accuracy, F1, AUC, confusion matrix)
- ✅ Rapport automatique sauvegardé
- ✅ Debugging facile (inspection des données)
- ✅ Contrôle total (modifier code, paramètres)
- ✅ Reproductibilité (configuration sauvegardée)

---

## 📚 Ressources

### Documentation
- **Notebook README** : `notebooks/README.md`
- **Inference Tracking** : `docs/INFERENCE_TRACKING.md`
- **API Documentation** : http://localhost:8000/docs

### Liens Externes
- **Sentence-Transformers** : https://www.sbert.net/
- **Cross-Encoder Tutorial** : https://www.sbert.net/examples/applications/cross-encoder/
- **Jupyter Documentation** : https://jupyter.org/documentation

---

## ✅ Checklist de Fine-Tuning

Avant de lancer le fine-tuning :

- [ ] MongoDB accessible et contient des données
- [ ] Au moins 50+ feedbacks collectés (100+ recommandé)
- [ ] Distribution équilibrée (≈50% like, ≈50% dislike)
- [ ] Jupyter installé : `pip install jupyter notebook`
- [ ] Dépendances installées : `pip install sentence-transformers torch ...`
- [ ] GPU disponible (recommandé mais optionnel)

Pendant le fine-tuning :

- [ ] Surveiller les métriques (pas de surapprentissage)
- [ ] Vérifier les visualisations
- [ ] S'assurer que l'amélioration est significative

Après le fine-tuning :

- [ ] Modèle sauvegardé dans `models/cross_encoder_finetuned/`
- [ ] Rapport généré : `training_report.txt`
- [ ] API redémarrée
- [ ] Modèle chargé (vérifier les logs)
- [ ] Tests effectués

---

## 🎉 Conclusion

Le fine-tuning via Jupyter Notebook offre une **expérience complète et professionnelle** pour améliorer votre modèle de reranking.

**Prochaine étape** : Lancez le notebook et commencez à améliorer votre système ! 🚀

```bash
cd notebooks
jupyter notebook
# Ouvrir fine_tune_cross_encoder.ipynb et exécuter !
```

---

**Créé le** : 8 décembre 2024  
**Version** : 1.0  
**Auteur** : EduRanker Development Team
