# 💼 PayrollPro - Système de Gestion de Paie Marocain

[![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

## 🌟 Description

**PayrollPro** est un système de gestion de paie moderne et complet, spécialement conçu pour les entreprises marocaines. Il respecte la législation sociale marocaine et s'intègre parfaitement avec les organismes officiels (CNSS, AMO, IR).

### ✨ Fonctionnalités Principales

🏢 **Gestion Multi-Sites**
- Gestion centralisée de plusieurs sites d'entreprise
- Départements et hiérarchies organisationnelles
- Reporting consolidé et par site

👥 **Gestion des Employés**
- Fichier personnel complet (CIN, CNSS, coordonnées)
- Historique des contrats et promotions
- Gestion des formations et compétences

💰 **Calcul de Paie Automatisé**
- Respect de la législation marocaine (CNSS, AMO, IR)
- Calcul automatique des cotisations sociales
- Gestion des primes et indemnités
- Heures supplémentaires et majorations

📊 **Tableaux de Bord Avancés**
- Interface moderne et intuitive
- Statistiques en temps réel
- Graphiques interactifs
- Alertes et notifications

📄 **Exports et Rapports**
- Bulletins de paie PDF
- Exports Excel CNSS
- Déclarations sociales
- Statistiques personnalisées

🔐 **Sécurité et Conformité**
- Authentification multi-niveaux
- Audit trail complet
- Respect RGPD
- Sauvegarde automatique

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- pip
- Git
- (Optionnel) PostgreSQL pour la production

### 1. Cloner le Projet
```bash
git clone https://github.com/votre-username/payrollpro.git
cd payrollpro
```

### 2. Environnement Virtuel
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Installation des Dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la Base de Données
```bash
python manage.py migrate
```

### 5. Créer des Données d'Exemple
```bash
python manage.py creer_donnees_exemple --employes 50
```

### 6. Lancer le Serveur
```bash
python manage.py runserver
```

### 7. Accéder à l'Application
- **Interface principale :** http://127.0.0.1:8000/
- **Administration :** http://127.0.0.1:8000/admin/

## 🔑 Comptes de Test

| Rôle | Username | Mot de passe | Description |
|------|----------|--------------|-------------|
| **Administrateur** | `admin` | `admin123` | Accès complet au système |
| **RH Manager** | `rh_manager` | `rh123` | Gestion du personnel et paie |
| **Employé** | `employe_test` | `emp123` | Consultation bulletins |

## 📱 Interfaces Modernes

### 🏢 Dashboard Administrateur
- Vue d'ensemble complète du système
- Statistiques en temps réel
- Gestion des utilisateurs et permissions
- Configuration système avancée

### 👥 Dashboard Ressources Humaines
- Gestion des employés et absences
- Validation des demandes
- Calcul et édition des paies
- Suivi des formations

### 💼 Interface Employé
- Consultation des bulletins de paie
- Demandes d'absences/congés
- Profil personnel
- Historique des paies

## 🛠 Structure du Projet

```
payrollpro/
├── 📁 gestion_paie/          # Configuration Django
│   ├── settings.py           # Paramètres de l'application
│   ├── urls.py              # URLs principales
│   └── wsgi.py              # Configuration WSGI
├── 📁 paie/                 # Application principale
│   ├── 📁 management/       # Commandes personnalisées
│   │   └── 📁 commands/
│   │       └── creer_donnees_exemple.py
│   ├── 📁 templates/        # Templates HTML
│   │   └── 📁 paie/
│   │       ├── base.html
│   │       ├── dashboard_admin_moderne.html
│   │       ├── dashboard_rh_moderne.html
│   │       └── connexion_simple.html
│   ├── models.py            # Modèles de données
│   ├── views.py             # Vues principales
│