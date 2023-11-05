# Modèles HuggingFace dans des Conteneurs Docker

## Aperçu
Ce projet offre un outil simple et efficace pour tester et déployer des modèles HuggingFace dans des conteneurs Docker. Actuellement en phase de développement initial, l'objectif est de fournir des API locales (non destinées à la production) pour divers modèles HuggingFace. Ces API facilitent l'expérimentation et l'évaluation des modèles par des appels successifs.

## Configuration Initiale
Pour utiliser ce projet, un fichier `.env` doit être présent à la racine du projet, spécifiant le chemin absolu vers le dossier du projet. Par exemple :

```python
HOST_PATH=/Volumes/CloudDatas/SynologyDrive/Docker/KwbHug/App/
```

## Démarrage et Accès
Le projet est configuré pour s'exécuter localement à l'adresse suivante : http://localhost:8000.

## Modèles Disponibles
À l'heure actuelle, un seul modèle est intégré et prêt à être utilisé :

- **Helsinki-NLP/opus-mt-fr-en** : Ce modèle est accessible via le port 8003 une fois installé.

## Endpoints API
Le modèle `Helsinki-NLP/opus-mt-fr-en` offre les endpoints suivants pour l'interaction :

- **POST /translate** : Accepte `text` comme paramètre requis pour la traduction.
- **GET /translate** : Version web pour la traduction.
