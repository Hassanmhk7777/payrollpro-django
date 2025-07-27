#!/usr/bin/env python
"""
Script pour corriger les problèmes de la page accueil_moderne
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_paie.settings')
django.setup()

def create_fixed_accueil_template():
    """Créer une version corrigée du template accueil_moderne"""
    
    print("🔧 CRÉATION DE LA VERSION CORRIGÉE")
    print("=" * 40)
    
    # Template corrigé avec meilleure gestion JavaScript
    fixed_template = '''{% extends 'paie/base.html' %}

{% block title %}PayrollPro - Système de Paie Moderne{% endblock %}

{% block extra_css %}
<style>
    /* Styles pour éviter le clignotement */
    .app-container {
        min-height: calc(100vh - 60px);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        opacity: 0;
        transition: opacity 0.5s ease-in-out;
    }
    
    .app-container.loaded {
        opacity: 1;
    }
    
    .nav-tabs-custom {
        background: white;
        border-radius: 15px 15px 0 0;
        padding: 1rem 1rem 0 1rem;
        border: none;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }

    .nav-tabs-custom .nav-link {
        border: none;
        background: transparent;
        color: #64748b;
        font-weight: 600;
        padding: 1rem 1.5rem;
        margin-right: 0.5rem;
        border-radius: 10px 10px 0 0;
        transition: all 0.3s ease;
    }

    .nav-tabs-custom .nav-link:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }

    .nav-tabs-custom .nav-link.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .content-area {
        background: white;
        border-radius: 0 0 15px 15px;
        min-height: 600px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        padding: 2rem;
    }

    .section-content {
        display: none;
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
    }

    .section-content.active {
        display: block;
        opacity: 1;
    }

    .loading-spinner {
        text-align: center;
        padding: 3rem;
        color: #667eea;
    }

    .dashboard-cards {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }

    .dashboard-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: transform 0.2s ease;
    }

    .dashboard-card:hover {
        transform: translateY(-5px);
    }

    .dashboard-card h3 {
        margin: 0;
        font-size: 2rem;
        font-weight: bold;
    }

    .dashboard-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }

    .error-message {
        text-align: center;
        padding: 2rem;
        color: #dc3545;
    }
</style>
{% endblock %}

{% block content %}
<div class="app-container" id="appContainer">
    <div class="container-fluid py-4">
        <!-- Navigation Tabs -->
        <div class="nav-tabs-custom">
            <ul class="nav nav-tabs" id="mainTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="dashboard-tab" data-bs-toggle="tab" 
                            data-bs-target="#dashboard" type="button" role="tab" 
                            aria-controls="dashboard" aria-selected="true"
                            onclick="switchToSection('dashboard')">
                        <i class="fas fa-tachometer-alt me-2"></i>Dashboard
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="employees-tab" data-bs-toggle="tab" 
                            data-bs-target="#employees" type="button" role="tab" 
                            aria-controls="employees" aria-selected="false"
                            onclick="switchToSection('employees')">
                        <i class="fas fa-users me-2"></i>Employés
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="payroll-tab" data-bs-toggle="tab" 
                            data-bs-target="#payroll" type="button" role="tab" 
                            aria-controls="payroll" aria-selected="false"
                            onclick="switchToSection('payroll')">
                        <i class="fas fa-calculator me-2"></i>Paie
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="rubriques-tab" data-bs-toggle="tab" 
                            data-bs-target="#rubriques" type="button" role="tab" 
                            aria-controls="rubriques" aria-selected="false"
                            onclick="switchToSection('rubriques')">
                        <i class="fas fa-list-alt me-2"></i>Rubriques
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="absences-tab" data-bs-toggle="tab" 
                            data-bs-target="#absences" type="button" role="tab" 
                            aria-controls="absences" aria-selected="false"
                            onclick="switchToSection('absences')">
                        <i class="fas fa-calendar-times me-2"></i>Absences
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="reports-tab" data-bs-toggle="tab" 
                            data-bs-target="#reports" type="button" role="tab" 
                            aria-controls="reports" aria-selected="false"
                            onclick="switchToSection('reports')">
                        <i class="fas fa-chart-bar me-2"></i>Rapports
                    </button>
                </li>
            </ul>
        </div>

        <!-- Content Area -->
        <div class="content-area">
            <div class="tab-content" id="mainTabContent">
                
                <!-- Dashboard Section -->
                <div class="section-content active" id="dashboard" role="tabpanel" aria-labelledby="dashboard-tab">
                    <div class="dashboard-cards">
                        <div class="dashboard-card">
                            <i class="fas fa-users fa-2x mb-3"></i>
                            <h3>{{ total_employes|default:0 }}</h3>
                            <p>Employés Actifs</p>
                        </div>
                        <div class="dashboard-card">
                            <i class="fas fa-calendar-times fa-2x mb-3"></i>
                            <h3>{{ absences_attente|default:0 }}</h3>
                            <p>Absences en Attente</p>
                        </div>
                        <div class="dashboard-card">
                            <i class="fas fa-money-bill-wave fa-2x mb-3"></i>
                            <h3>{{ masse_salariale|floatformat:0|default:0 }} DH</h3>
                            <p>Masse Salariale</p>
                        </div>
                        <div class="dashboard-card">
                            <i class="fas fa-user-plus fa-2x mb-3"></i>
                            <h3>{{ nouveaux_employes|default:0 }}</h3>
                            <p>Nouveaux ce Mois</p>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5><i class="fas fa-chart-line me-2"></i>Évolution des Effectifs</h5>
                                </div>
                                <div class="card-body">
                                    <p class="text-muted">Graphique des effectifs sur les 12 derniers mois...</p>
                                    <canvas id="effectifsChart" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5><i class="fas fa-tasks me-2"></i>Actions Rapides</h5>
                                </div>
                                <div class="card-body">
                                    <div class="d-grid gap-2">
                                        <button class="btn btn-primary" onclick="switchToSection('employees')">
                                            <i class="fas fa-user-plus me-2"></i>Ajouter un Employé
                                        </button>
                                        <button class="btn btn-success" onclick="switchToSection('payroll')">
                                            <i class="fas fa-calculator me-2"></i>Calculer la Paie
                                        </button>
                                        <button class="btn btn-info" onclick="switchToSection('rubriques')">
                                            <i class="fas fa-list-alt me-2"></i>Gérer les Rubriques
                                        </button>
                                        <button class="btn btn-warning" onclick="switchToSection('reports')">
                                            <i class="fas fa-download me-2"></i>Exporter les Données
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Other Sections -->
                <div class="section-content" id="employees" role="tabpanel" aria-labelledby="employees-tab">
                    <div class="loading-spinner">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                        <p class="mt-3">Chargement du module employés...</p>
                    </div>
                </div>

                <div class="section-content" id="payroll" role="tabpanel" aria-labelledby="payroll-tab">
                    <div class="loading-spinner">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                        <p class="mt-3">Chargement du module paie...</p>
                    </div>
                </div>

                <div class="section-content" id="rubriques" role="tabpanel" aria-labelledby="rubriques-tab">
                    <div class="loading-spinner">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                        <p class="mt-3">Chargement du module rubriques...</p>
                    </div>
                </div>

                <div class="section-content" id="absences" role="tabpanel" aria-labelledby="absences-tab">
                    <div class="loading-spinner">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                        <p class="mt-3">Chargement du module absences...</p>
                    </div>
                </div>

                <div class="section-content" id="reports" role="tabpanel" aria-labelledby="reports-tab">
                    <div class="loading-spinner">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Chargement...</span>
                        </div>
                        <p class="mt-3">Chargement du module rapports...</p>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<!-- Toast Container -->
<div class="toast-container position-fixed bottom-0 end-0 p-3">
    <div id="notificationToast" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
            <i class="fas fa-info-circle text-primary me-2"></i>
            <strong class="me-auto">PayrollPro</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body" id="toastMessage">
            Message de notification
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// Variables globales
let currentSection = 'dashboard';
let loadedSections = ['dashboard']; // Dashboard est déjà chargé
let isLoading = false;

// Configuration API endpoints
const API_ENDPOINTS = {
    'employees': '/api/spa/employees/',
    'payroll': '/api/spa/payroll/',
    'rubriques': '/api/spa/rubriques/',
    'absences': '/api/spa/absences/',
    'reports': '/api/spa/reports/'
};

// Fonction pour afficher des notifications
function showNotification(message, type = 'info') {
    const toast = document.getElementById('notificationToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastHeader = toast.querySelector('.toast-header i');
    
    // Configurer l'icône selon le type
    toastHeader.className = `fas me-2 ${
        type === 'success' ? 'fa-check-circle text-success' :
        type === 'error' ? 'fa-exclamation-triangle text-danger' :
        type === 'warning' ? 'fa-exclamation-circle text-warning' :
        'fa-info-circle text-primary'
    }`;
    
    toastMessage.textContent = message;
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Fonction pour changer de section avec meilleure gestion
function switchToSection(sectionName) {
    console.log(`🔄 Changement vers la section: ${sectionName}`);
    
    // Éviter les changements multiples simultanés
    if (isLoading) {
        console.log('⚠️ Changement en cours, ignoré');
        return;
    }
    
    // Masquer toutes les sections
    document.querySelectorAll('.section-content').forEach(section => {
        section.classList.remove('active');
    });
    
    // Afficher la section cible
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.classList.add('active');
        currentSection = sectionName;
        
        // Charger le contenu si nécessaire
        if (!loadedSections.includes(sectionName) && API_ENDPOINTS[sectionName]) {
            loadSectionContent(sectionName);
        }
    } else {
        console.error(`❌ Section non trouvée: ${sectionName}`);
        showNotification(`Section "${sectionName}" non trouvée`, 'error');
    }
}

// Fonction pour charger le contenu d'une section via AJAX
function loadSectionContent(sectionName) {
    console.log(`📡 Chargement du contenu pour: ${sectionName}`);
    
    const endpoint = API_ENDPOINTS[sectionName];
    if (!endpoint) {
        console.error(`❌ Aucun endpoint API pour: ${sectionName}`);
        return;
    }
    
    const section = document.getElementById(sectionName);
    if (!section) {
        console.error(`❌ Section DOM non trouvée: ${sectionName}`);
        return;
    }
    
    isLoading = true;
    
    // Effectuer la requête AJAX
    fetch(endpoint, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        console.log(`📡 Réponse API pour ${sectionName}: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Vérifier le type de contenu
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        } else {
            // Si c'est du HTML directement
            return response.text().then(html => ({ success: true, content: html }));
        }
    })
    .then(data => {
        console.log(`✅ Contenu chargé pour ${sectionName}`);
        
        if (data.success !== false) {
            // Remplacer le contenu de la section
            section.innerHTML = data.content || data;
            
            // Marquer comme chargé
            if (!loadedSections.includes(sectionName)) {
                loadedSections.push(sectionName);
            }
            
            showNotification(`Module "${getSectionDisplayName(sectionName)}" chargé`, 'success');
        } else {
            throw new Error(data.error || 'Erreur inconnue');
        }
    })
    .catch(error => {
        console.error(`❌ Erreur chargement ${sectionName}:`, error);
        
        // Afficher un message d'erreur dans la section
        section.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                <h4>Erreur de chargement</h4>
                <p>Impossible de charger le module "${getSectionDisplayName(sectionName)}"</p>
                <p class="text-muted">Erreur: ${error.message}</p>
                <button class="btn btn-primary mt-3" onclick="loadSectionContent('${sectionName}')">
                    <i class="fas fa-redo me-2"></i>Réessayer
                </button>
            </div>
        `;
        
        showNotification(`Erreur lors du chargement de "${getSectionDisplayName(sectionName)}"`, 'error');
    })
    .finally(() => {
        isLoading = false;
    });
}

// Fonction pour obtenir le nom d'affichage d'une section
function getSectionDisplayName(sectionName) {
    const names = {
        'dashboard': 'Dashboard',
        'employees': 'Employés',
        'payroll': 'Paie',
        'rubriques': 'Rubriques',
        'absences': 'Absences',
        'reports': 'Rapports'
    };
    return names[sectionName] || sectionName;
}

// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 PayrollPro SPA - Initialisation');
    
    // Afficher l'interface progressivement pour éviter le clignotement
    setTimeout(() => {
        const appContainer = document.getElementById('appContainer');
        if (appContainer) {
            appContainer.classList.add('loaded');
        }
    }, 100);
    
    // Gérer les paramètres d'URL
    const urlParams = new URLSearchParams(window.location.search);
    const sectionParam = urlParams.get('section');
    
    if (sectionParam && API_ENDPOINTS[sectionParam]) {
        console.log(`🔗 Paramètre URL détecté: ${sectionParam}`);
        setTimeout(() => {
            switchToSection(sectionParam);
        }, 500);
    }
    
    // Gérer le hash de l'URL
    const hash = window.location.hash.substring(1);
    if (hash && API_ENDPOINTS[hash] && !sectionParam) {
        console.log(`🔗 Hash URL détecté: ${hash}`);
        setTimeout(() => {
            switchToSection(hash);
        }, 500);
    }
    
    console.log('✅ PayrollPro SPA - Initialisé avec succès');
});

// Rendre les fonctions accessibles globalement
window.switchToSection = switchToSection;
window.loadSectionContent = loadSectionContent;
window.showNotification = showNotification;

// Gestion des erreurs globales
window.addEventListener('error', function(event) {
    console.error('❌ Erreur JavaScript globale:', event.error);
    showNotification('Une erreur inattendue s\'est produite', 'error');
});

// Gestion des promesses rejetées
window.addEventListener('unhandledrejection', function(event) {
    console.error('❌ Promesse rejetée non gérée:', event.reason);
    showNotification('Erreur de communication avec le serveur', 'error');
});
</script>
{% endblock %}'''
    
    # Sauvegarder le template corrigé
    template_path = 'paie/templates/paie/accueil_moderne_fixed.html'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(fixed_template)
    
    print(f"✅ Template corrigé créé: {template_path}")
    return template_path

def create_fixed_view():
    """Créer une vue corrigée pour accueil_moderne"""
    
    print("🔧 MISE À JOUR DE LA VUE")
    print("=" * 25)
    
    # Lire le fichier views.py
    with open('paie/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter une nouvelle vue corrigée
    new_view = """
@login_required
def accueil_moderne_fixed(request):
    \"\"\"Page d'accueil SPA moderne - Version corrigée\"\"\"
    
    try:
        # Statistiques pour le dashboard
        total_employes = Employe.objects.filter(actif=True).count()
        
        # Absences en attente
        absences_attente = 0
        try:
            from .models import Absence
            absences_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
        except:
            pass
        
        # Calcul de la masse salariale
        employes_actifs = Employe.objects.filter(actif=True)
        masse_salariale = sum(employe.salaire_base for employe in employes_actifs)
        
        # Nouveaux employés du mois
        from datetime import datetime
        debut_mois = datetime.now().replace(day=1)
        nouveaux_employes = Employe.objects.filter(
            date_embauche__gte=debut_mois,
            actif=True
        ).count()
        
        context = {
            'total_employes': total_employes,
            'absences_attente': absences_attente,
            'masse_salariale': masse_salariale,
            'nouveaux_employes': nouveaux_employes,
        }
        
        return render(request, 'paie/accueil_moderne_fixed.html', context)
        
    except Exception as e:
        # En cas d'erreur, rediriger vers une page simple
        messages.error(request, f'Erreur lors du chargement du dashboard: {str(e)}')
        return redirect('admin:index')
"""
    
    # Ajouter la nouvelle vue au fichier
    if 'def accueil_moderne_fixed' not in content:
        content += new_view
        
        with open('paie/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Vue corrigée ajoutée à views.py")
    else:
        print("⚠️ Vue corrigée déjà présente")

def update_urls():
    """Mettre à jour les URLs pour inclure la version corrigée"""
    
    print("🔧 MISE À JOUR DES URLS")
    print("=" * 22)
    
    # Lire le fichier urls.py
    with open('paie/urls.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter la nouvelle route
    new_url = "    path('accueil_moderne_fixed/', views.accueil_moderne_fixed, name='accueil_moderne_fixed'),"
    
    if 'accueil_moderne_fixed' not in content:
        # Trouver où insérer la nouvelle URL
        lines = content.split('\\n')
        for i, line in enumerate(lines):
            if "path('accueil_moderne/" in line:
                lines.insert(i + 1, new_url)
                break
        
        content = '\\n'.join(lines)
        
        with open('paie/urls.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ URL corrigée ajoutée")
        print("📍 Nouvelle route: /accueil_moderne_fixed/")
    else:
        print("⚠️ URL corrigée déjà présente")

if __name__ == "__main__":
    create_fixed_accueil_template()
    create_fixed_view()
    update_urls()
    
    print("\\n🎉 CORRECTION TERMINÉE")
    print("=" * 25)
    print("✅ Template corrigé créé")
    print("✅ Vue corrigée ajoutée") 
    print("✅ URL corrigée configurée")
    print("\\n📍 Testez maintenant avec: http://127.0.0.1:8000/accueil_moderne_fixed/")
    print("\\n💡 Améliorations apportées:")
    print("   • Suppression des redirections automatiques")
    print("   • Meilleure gestion des erreurs JavaScript")
    print("   • Délais d'attente appropriés")
    print("   • Chargement progressif pour éviter le clignotement")
    print("   • Gestion robuste des appels AJAX")
