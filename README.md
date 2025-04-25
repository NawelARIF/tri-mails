### 📬 Tri Automatique d'E-mails Gmail par IA Locale et Détection d'Inactivité

## Table des matières 

- [Description](#description)
- [Pré-requis](#pré-requis)
- [Structure du projet](#structure)
- [API Gmail](#APIGmail)
- [Auteurs](#auteurs)


## Description

Ce projet a été développé avec pour objectif de créer une solution autonome et intelligente de tri d'e-mails Gmail, exploitant :

  - L'analyse locale de texte via un LLM léger (Ollama – modèle Mistral), 
  - L'API Gmail pour l'organisation automatique des messages,
  -  La détection passive d'inactivité de l'utilisateur pour un déclenchement sans intervention.

 ## Pré-requis

Avant de commencer, assurez-vous d’avoir les éléments suivants installés et configurés sur votre machine :

1. **Python 3.13**  
   - Téléchargez la dernière version sur le site officiel : <https://www.python.org/downloads/>  
   - Vérifiez l’installation : `python3 --version`

2. **Ollama (modèle : Mistral)**  
   - Installez Ollama depuis <https://ollama.com/>  
   - Lancez le service en local : `ollama run mistral`  
   - Vérifiez que l’API répond sur `http://localhost:11434`

3. **Bibliothèques Python nécessaires**  
   ```bash
   pip install google-api-python-client google-auth requests beautifulsoup4 pynput

  

## 🛠️ Structure du Projet

## 1. Configuration de l'API Gmail 


**Créer les identifiants pour l'API Gmail**

- Créez un projet dans la Google Cloud Console [Google Cloud Console](https://console.cloud.google.com/).
- Activez l'API Gmail pour ce projet.
- Téléchargez le fichier credentials.json et placez-le dans le répertoire principal ou dans un dossier config/.


## 2. Connexion et Scrapping des e-mails

Utilisation de google-api-python-client pour :

  - Se connecter à la boîte mail.
  - Récupérer les 50 derniers e-mails sous format brut ou HTML.

Pourquoi ? Pouvoir lire rapidement un volume pertinent de messages récents pour analyse et tri sans surcharger le traitement.

## 3Nettoyage du contenu pour préparation à l'analyse

  Application de BeautifulSoup pour :
  
  - Nettoyer tout le HTML résiduel.
  - Recupérez uniquement le texte exploitable.

## 4. Classification locale avec Ollama

  Implémentation d'une analyse intelligente :
  
  - Envoi du sujet et d'un extrait du corps du mail à Ollama via requête HTTP locale.
  - Utilisation du modèle Mistral.
  - Classification parmi 4 catégories : emploi, shopping, publicité, autres.


## 5. Déclenchement automatique par surveillance souris

Intégration de pynput pour :

  - Écouter les mouvements souris en arrière-plan.
  - Détecter 120 secondes d'inactivité.
  - Déclencher le tri automatiquement.

Pourquoi ? Créer un assistant totalement passif : l'utilisateur continue ses activités normales sans même avoir à penser à lancer le script.


## 👨‍💻 Auteur

  Nawel ARIF
  Ali BOUGUERRA
