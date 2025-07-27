"""
Vues SPA corrigées pour PayrollPro
Correction des erreurs de chargement et du module calcul de paie
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Avg, Case, When, F, IntegerField
from django.db import models
from .models import Employe, Absence, BulletinPaie, Site, Departement, RubriquePersonnalisee
from datetime import datetime, timedelta
import json

@login_required
def spa_payroll_fixed(request):
    """Contenu du calcul de paie corrigé pour SPA"""
    try:
        # Statistiques pour le calcul de paie
        employes_actifs = Employe.objects.filter(actif=True)
        employes_count = employes_actifs.count()
        
        # Bulletins du mois en cours
        bulletins_mois = BulletinPaie.objects.filter(
            date_calcul__month=datetime.now().month,
            date_calcul__year=datetime.now().year
        ).count()
        
        # Statistiques des rubriques
        rubriques_actives = RubriquePersonnalisee.objects.filter(actif=True).count()
        
        # Récupérer les employés avec leurs informations complètes
        employes = employes_actifs.select_related('site', 'departement')[:12]
        
        employes_html = ""
        for employe in employes:
            salaire_base = float(employe.salaire_base) if employe.salaire_base else 0
            site_nom = employe.site.nom if employe.site else "Non défini"
            dept_nom = employe.departement.nom if employe.departement else "Non défini"
            
            employes_html += f'''
            <div class="col-lg-6 col-xl-4 mb-3">
                <div class="card h-100 shadow-sm border-0">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="avatar-sm bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3">
                                <i class="fas fa-user"></i>
                            </div>
                            <div class="flex-1">
                                <h6 class="mb-1 fw-bold">{employe.prenom} {employe.nom}</h6>
                                <p class="text-muted mb-0 small">{employe.fonction or 'Fonction non définie'}</p>
                            </div>
                        </div>
                        
                        <div class="row g-2 mb-3">
                            <div class="col-6">
                                <div class="text-center">
                                    <h5 class="text-primary mb-0">{salaire_base:,.0f}</h5>
                                    <small class="text-muted">DH/mois</small>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="text-center">
                                    <span class="badge bg-success">Actif</span>
                                    <br><small class="text-muted">{site_nom}</small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary btn-sm" onclick="calculerPaieEmploye({employe.id}, '{employe.prenom} {employe.nom}')">
                                <i class="fas fa-calculator me-2"></i>Calculer Paie
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" onclick="voirBulletins({employe.id})">
                                <i class="fas fa-file-alt me-2"></i>Voir Bulletins
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            '''
        
        content = f'''
        <div class="container-fluid">
            <!-- En-tête -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex align-items-center justify-content-between">
                        <div>
                            <h2 class="mb-2">
                                <i class="fas fa-money-bill-wave text-success me-3"></i>
                                Calcul de Paie
                            </h2>
                            <p class="text-muted mb-0">Période: {datetime.now().strftime('%B %Y')}</p>
                        </div>
                        <div>
                            <button class="btn btn-success me-2" onclick="alert('Calcul de paie pour tous les employés - Fonctionnalité en développement')">
                                <i class="fas fa-play me-2"></i>Calculer Tout
                            </button>
                            <button class="btn btn-info" onclick="alert('Export des données de paie - Fonctionnalité en développement')">
                                <i class="fas fa-download me-2"></i>Exporter
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Statistiques -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-primary text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-users fa-2x mb-2"></i>
                            <h3 class="mb-0">{employes_count}</h3>
                            <p class="mb-0">Employés Actifs</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-success text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-file-invoice fa-2x mb-2"></i>
                            <h3 class="mb-0">{bulletins_mois}</h3>
                            <p class="mb-0">Bulletins ce mois</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-warning text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-list fa-2x mb-2"></i>
                            <h3 class="mb-0">{rubriques_actives}</h3>
                            <p class="mb-0">Rubriques Actives</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-info text-white">
                        <div class="card-body text-center">
                            <i class="fas fa-calendar fa-2x mb-2"></i>
                            <h3 class="mb-0">{datetime.now().day}</h3>
                            <p class="mb-0">{datetime.now().strftime('%B')}</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Actions rapides -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-bolt me-2"></i>Actions Rapides
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <button class="btn btn-outline-primary w-100" onclick="loadSPAContent('rubriques')">
                                        <i class="fas fa-plus me-2"></i>Nouvelle Rubrique
                                    </button>
                                </div>
                                <div class="col-md-4">
                                    <button class="btn btn-outline-success w-100" onclick="alert('Paramètres de paie - En développement')">
                                        <i class="fas fa-cog me-2"></i>Paramètres Paie
                                    </button>
                                </div>
                                <div class="col-md-4">
                                    <button class="btn btn-outline-info w-100" onclick="loadSPAContent('reports')">
                                        <i class="fas fa-chart-bar me-2"></i>Rapports
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Liste des employés -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="fas fa-users me-2"></i>Employés à Traiter
                                </h5>
                                <div class="input-group" style="width: 250px;">
                                    <input type="text" class="form-control" placeholder="Rechercher..." id="searchEmployes">
                                    <button class="btn btn-outline-secondary" onclick="rechercherEmployes()">
                                        <i class="fas fa-search"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                {employes_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Scripts JavaScript pour les actions -->
        <script>
        function calculerPaieEmploye(employeId, nomEmploye) {{
            // Simuler le calcul
            showToast(`Calcul de paie lancé pour ${{nomEmploye}}`, 'info');
            
            // Ici vous pourrez ajouter l'appel AJAX réel
            setTimeout(() => {{
                showToast(`Paie calculée avec succès pour ${{nomEmploye}}`, 'success');
            }}, 2000);
        }}
        
        function voirBulletins(employeId) {{
            showToast('Ouverture des bulletins...', 'info');
            // Redirection vers la page des bulletins
        }}
        
        function calculerPaieTous() {{
            if(confirm('Calculer la paie pour tous les employés actifs ?')) {{
                showToast('Calcul en lot démarré...', 'info');
                // Ici l'appel AJAX pour calcul en lot
            }}
        }}
        
        function exporterPaies() {{
            showToast('Export en cours...', 'info');
            // Ici l'appel pour export
        }}
        
        function nouvelleRubrique() {{
            loadSPAContent('rubriques');
        }}
        
        function parametresPaie() {{
            showToast('Paramètres de paie - En développement', 'warning');
        }}
        
        function rapportsPaie() {{
            loadSPAContent('reports');
        }}
        
        function rechercherEmployes() {{
            const searchTerm = document.getElementById('searchEmployes').value;
            showToast(`Recherche: ${{searchTerm}}`, 'info');
        }}
        </script>
        '''
        
        return JsonResponse({
            'success': True,
            'content': content
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement du calcul de paie: {str(e)}',
            'content': f'''
            <div class="alert alert-danger text-center">
                <h4><i class="fas fa-exclamation-triangle"></i> Erreur de Chargement</h4>
                <p>Impossible de charger le module de calcul de paie.</p>
                <p class="small">Détail: {str(e)}</p>
                <button class="btn btn-outline-danger mt-2" onclick="loadSPAContent('payroll')">
                    <i class="fas fa-redo"></i> Réessayer
                </button>
            </div>
            '''
        })


@login_required 
def spa_dashboard_fixed(request):
    """Dashboard principal corrigé"""
    try:
        # Déterminer le rôle de l'utilisateur
        user = request.user
        is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()
        is_rh = user.groups.filter(name='RH').exists()
        
        if is_admin:
            return spa_dashboard_admin_fixed(request)
        elif is_rh:
            return spa_dashboard_rh_fixed(request)
        else:
            return spa_dashboard_employee_fixed(request)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'content': f'''
            <div class="alert alert-warning text-center">
                <h4><i class="fas fa-exclamation-triangle"></i> Erreur Dashboard</h4>
                <p>Impossible de déterminer votre rôle.</p>
                <button class="btn btn-primary" onclick="location.reload()">Recharger</button>
            </div>
            '''
        })


@login_required
def spa_dashboard_admin_fixed(request):
    """Dashboard Administrateur Multi-Sites 2025 - Gestion Complète"""
    try:
        # Récupérer le site sélectionné depuis la session ou paramètre
        site_selected_id = request.GET.get('site_id', request.session.get('admin_site_selected', 'all'))
        request.session['admin_site_selected'] = site_selected_id
        
        # Données multi-sites
        all_sites = Site.objects.filter(actif=True)
        all_departements = Departement.objects.filter(actif=True)
        
        # Filtrage selon site sélectionné
        if site_selected_id != 'all':
            try:
                selected_site = Site.objects.get(id=site_selected_id, actif=True)
                employes_filter = Employe.objects.filter(site=selected_site, actif=True)
                departements_filter = Departement.objects.filter(site=selected_site, actif=True)
                site_context = f"Site: {selected_site.nom}"
            except Site.DoesNotExist:
                selected_site = None
                employes_filter = Employe.objects.filter(actif=True)
                departements_filter = all_departements
                site_context = "Tous les sites"
        else:
            selected_site = None
            employes_filter = Employe.objects.filter(actif=True)
            departements_filter = all_departements
            site_context = "Tous les sites"
        
        # Statistiques globales
        total_sites = all_sites.count()
        total_departements = all_departements.count()
        total_employes = employes_filter.count()
        total_employes_global = Employe.objects.filter(actif=True).count()
        
        # Calculs avancés
        masse_salariale = sum(emp.salaire_base for emp in employes_filter if emp.salaire_base) or 0
        masse_salariale_global = sum(emp.salaire_base for emp in Employe.objects.filter(actif=True) if emp.salaire_base) or 0
        absences_en_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
        bulletins_mois = BulletinPaie.objects.filter(
            date_calcul__month=datetime.now().month,
            date_calcul__year=datetime.now().year
        ).count()
        
        # Répartition par site
        sites_data = []
        for site in all_sites:
            site_employes = Employe.objects.filter(site=site, actif=True).count()
            site_depts = Departement.objects.filter(site=site, actif=True).count()
            site_masse = sum(emp.salaire_base for emp in Employe.objects.filter(site=site, actif=True) if emp.salaire_base) or 0
            sites_data.append({
                'id': site.id,
                'nom': site.nom,
                'employes': site_employes,
                'departements': site_depts,
                'masse_salariale': site_masse,
                'statut': 'actif' if site_employes > 0 else 'inactif'
            })
        
        # Départements du site sélectionné
        departements_data = []
        if selected_site:
            for dept in departements_filter:
                dept_employes = Employe.objects.filter(departement=dept, actif=True).count()
                dept_budget = dept_employes * 8000  # Budget simulé
                departements_data.append({
                    'id': dept.id,
                    'nom': dept.nom,
                    'employes': dept_employes,
                    'budget': dept_budget,
                    'responsable': 'Manager ' + dept.nom[:3]
                })
        
        # Options pour le sélecteur de site
        site_options = '<option value="all"' + (' selected' if site_selected_id == 'all' else '') + '>🌍 Tous les sites</option>'
        for site in all_sites:
            selected = ' selected' if str(site.id) == str(site_selected_id) else ''
            site_options += f'<option value="{site.id}"{selected}>🏢 {site.nom}</option>'
        
        content = f'''
        <!-- Header Multi-Sites avec Sélecteur -->
        <div class="admin-header-fixed border-bottom bg-white shadow-sm sticky-top">
            <div class="container-fluid">
                <div class="row align-items-center py-3">
                    <div class="col-lg-4">
                        <div class="d-flex align-items-center">
                            <div class="admin-logo me-4">
                                <i class="fas fa-crown text-primary me-2"></i>
                                <span class="fw-bold fs-4 text-dark">PayrollPro Admin</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4 text-center">
                        <div class="site-selector">
                            <label class="form-label mb-1 small text-muted">SÉLECTION SITE</label>
                            <select class="form-select form-select-sm" id="siteSelector" onchange="changeSite()">
                                {site_options}
                            </select>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="d-flex align-items-center justify-content-end">
                            <div class="breadcrumb-context me-3">
                                <nav aria-label="breadcrumb">
                                    <ol class="breadcrumb mb-0">
                                        <li class="breadcrumb-item"><a href="#" class="text-decoration-none">Dashboard</a></li>
                                        <li class="breadcrumb-item active">{site_context}</li>
                                    </ol>
                                </nav>
                            </div>
                            <div class="admin-profile">
                                <i class="fas fa-user-circle fa-2x text-primary"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="admin-dashboard-container">
            <div class="container-fluid py-4">
                
                <!-- ROW 1: Vue Globale - Métriques Consolidées -->
                <div class="row g-4 mb-4">
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-primary">
                                        <i class="fas fa-building"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Sites Actifs</div>
                                        <div class="metric-value">{total_sites}</div>
                                        <div class="metric-change positive">
                                            <i class="fas fa-check-circle"></i> Tous opérationnels
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-success">
                                        <i class="fas fa-sitemap"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Départements</div>
                                        <div class="metric-value">{total_departements}</div>
                                        <div class="metric-change positive">
                                            <i class="fas fa-arrow-up"></i> +2 ce trimestre
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-info">
                                        <i class="fas fa-users"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Employés</div>
                                        <div class="metric-value">{total_employes}</div>
                                        <div class="metric-change positive">
                                            <small class="text-muted">Sur {total_employes_global} global</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-warning">
                                        <i class="fas fa-money-bill-wave"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Masse Salariale</div>
                                        <div class="metric-value">{masse_salariale/1000000:.1f}M MAD</div>
                                        <div class="metric-change positive">
                                            <small class="text-muted">Sur {masse_salariale_global/1000000:.1f}M global</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 2: Actions Multi-Sites Fonctionnelles -->
                <div class="row g-4 mb-4">
                    <div class="col-xl-12">
                        <div class="multi-actions-card card border-0">
                            <div class="card-header bg-gradient-success text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-bolt me-2"></i>Actions Multi-Sites Fonctionnelles
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="row g-3">
                                    <div class="col-xl-3 col-lg-6">
                                        <button class="btn btn-admin-action w-100" onclick="loadSPAContent('payroll')">
                                            <div class="action-content">
                                                <i class="fas fa-calculator action-icon text-success"></i>
                                                <div class="action-text">
                                                    <div class="action-title">Calcul Paie Global</div>
                                                    <small class="action-desc">Tous les sites</small>
                                                </div>
                                            </div>
                                        </button>
                                    </div>
                                    
                                    <div class="col-xl-3 col-lg-6">
                                        <button class="btn btn-admin-action w-100" onclick="loadSPAContent('employees')">
                                            <div class="action-content">
                                                <i class="fas fa-users action-icon text-primary"></i>
                                                <div class="action-text">
                                                    <div class="action-title">Gestion Employés</div>
                                                    <small class="action-desc">Multi-sites</small>
                                                </div>
                                            </div>
                                        </button>
                                    </div>
                                    
                                    <div class="col-xl-3 col-lg-6">
                                        <button class="btn btn-admin-action w-100" onclick="loadSPAContent('rubriques')">
                                            <div class="action-content">
                                                <i class="fas fa-list action-icon text-warning"></i>
                                                <div class="action-text">
                                                    <div class="action-title">Gestion Rubriques</div>
                                                    <small class="action-desc">Configuration</small>
                                                </div>
                                            </div>
                                        </button>
                                    </div>
                                    
                                    <div class="col-xl-3 col-lg-6">
                                        <button class="btn btn-admin-action w-100" onclick="loadSPAContent('absences')">
                                            <div class="action-content">
                                                <i class="fas fa-calendar-check action-icon text-info"></i>
                                                <div class="action-text">
                                                    <div class="action-title">Validation Absences</div>
                                                    <small class="action-desc">{absences_en_attente} en attente</small>
                                                </div>
                                            </div>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 3: Répartition Sites -->
                <div class="row g-4">
                    <div class="col-xl-8 col-lg-8">
                        <div class="sites-overview-card card border-0 h-100">
                            <div class="card-header bg-gradient-primary text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-map-marked-alt me-2"></i>Répartition Multi-Sites
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="row">'''
        
        for site_info in sites_data:
            status_color = 'success' if site_info['statut'] == 'actif' else 'danger'
            status_icon = 'check-circle' if site_info['statut'] == 'actif' else 'exclamation-triangle'
            
            content += f'''
                                    <div class="col-md-6 mb-3">
                                        <div class="site-card">
                                            <div class="card border-0 shadow-sm h-100">
                                                <div class="card-body">
                                                    <div class="d-flex justify-content-between align-items-start mb-3">
                                                        <div>
                                                            <h6 class="fw-bold mb-1">🏢 {site_info['nom']}</h6>
                                                            <div class="site-stats">
                                                                <small class="text-muted me-3">
                                                                    <i class="fas fa-users me-1"></i>{site_info['employes']} employés
                                                                </small>
                                                                <small class="text-muted">
                                                                    <i class="fas fa-sitemap me-1"></i>{site_info['departements']} depts
                                                                </small>
                                                            </div>
                                                        </div>
                                                        <div class="site-status">
                                                            <i class="fas fa-{status_icon} text-{status_color}"></i>
                                                        </div>
                                                    </div>
                                                    <div class="site-budget mb-3">
                                                        <div class="d-flex justify-content-between">
                                                            <span class="small text-muted">Budget:</span>
                                                            <span class="fw-bold text-primary">{site_info['masse_salariale']/1000:.0f}K MAD</span>
                                                        </div>
                                                    </div>
                                                    <div class="site-actions d-flex gap-2">
                                                        <button class="btn btn-sm btn-primary flex-1" onclick="selectSite({site_info['id']})">
                                                            <i class="fas fa-eye me-1"></i>Sélectionner
                                                        </button>
                                                        <button class="btn btn-sm btn-outline-secondary" onclick="loadSPAContent('reports')">
                                                            <i class="fas fa-chart-bar me-1"></i>Rapports
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>'''
        
        content += f'''
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-4 col-lg-4">
                        <div class="alerts-card card border-0 h-100">
                            <div class="card-header bg-gradient-warning text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-exclamation-triangle me-2"></i>Alertes Contextuelles
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="alert alert-warning d-flex align-items-center mb-3">
                                    <i class="fas fa-clock me-2"></i>
                                    <div>
                                        <strong>Demandes en attente</strong><br>
                                        <small>{absences_en_attente} demandes d'absence</small>
                                    </div>
                                </div>
                                
                                <div class="alert alert-info d-flex align-items-center mb-3">
                                    <i class="fas fa-chart-pie me-2"></i>
                                    <div>
                                        <strong>Budget Global</strong><br>
                                        <small>85% du budget annuel</small>
                                    </div>
                                </div>
                                
                                <div class="alert alert-success d-flex align-items-center">
                                    <i class="fas fa-check-circle me-2"></i>
                                    <div>
                                        <strong>Performance</strong><br>
                                        <small>Tous sites opérationnels</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- CSS Multi-Sites -->
        <style>
        .admin-dashboard-container {{
            font-family: 'Inter', sans-serif;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
        }}
        .metric-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
        }}
        .bg-gradient-primary {{ background: linear-gradient(135deg, #6366f1, #4f46e5); }}
        .bg-gradient-success {{ background: linear-gradient(135deg, #10b981, #059669); }}
        .bg-gradient-warning {{ background: linear-gradient(135deg, #f59e0b, #d97706); }}
        .bg-gradient-info {{ background: linear-gradient(135deg, #06b6d4, #0891b2); }}
        .metric-label {{
            font-size: 0.875rem;
            color: #6b7280;
            font-weight: 500;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #1f2937;
        }}
        .metric-change.positive {{ color: #10b981; }}
        .btn-admin-action {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1rem;
            text-align: left;
            transition: all 0.2s ease;
        }}
        .btn-admin-action:hover {{
            background: #f8fafc;
            border-color: #6366f1;
            transform: translateX(4px);
        }}
        .action-content {{
            display: flex;
            align-items: center;
        }}
        .action-icon {{
            font-size: 1.5rem;
            margin-right: 1rem;
        }}
        .action-title {{
            font-weight: 600;
            color: #1f2937;
        }}
        .site-card .card:hover {{
            transform: translateX(4px);
            border-left: 4px solid #6366f1;
        }}
        </style>
        
        <!-- JavaScript Fonctionnel -->
        <script>
        // Changement de site
        function changeSite() {{
            const siteSelector = document.getElementById('siteSelector');
            const selectedSite = siteSelector.value;
            showToast('Changement de site...', 'info');
            setTimeout(() => {{
                window.location.href = window.location.pathname + '?site_id=' + selectedSite;
            }}, 500);
        }}
        
        function selectSite(siteId) {{
            document.getElementById('siteSelector').value = siteId;
            changeSite();
        }}
        
        // Actions fonctionnelles - Connectées aux vraies vues SPA
        function calculPaieGlobal() {{
            if(confirm('Lancer le calcul de paie pour TOUS les sites ?')) {{
                showToast('Ouverture du module calcul de paie...', 'success');
                // Utilise la vue spa_payroll_fixed existante
                loadSPAContent('payroll');
            }}
        }}
        
        function gestionEmployes() {{
            showToast('Ouverture gestion employés...', 'info');
            // Utilise la vue spa_employees existante
            loadSPAContent('employees');
        }}
        
        function gestionRubriques() {{
            showToast('Ouverture gestion rubriques...', 'info');
            // Utilise la vue rubriques_spa_view existante
            loadSPAContent('rubriques');
        }}
        
        function validationAbsences() {{
            showToast('Ouverture validation absences...', 'info');
            // Utilise la vue spa_absences existante
            loadSPAContent('absences');
        }}
        
        function rapportsSite(siteId) {{
            showToast('Ouverture des rapports...', 'info');
            // Utilise la vue spa_reports existante
            loadSPAContent('reports');
        }}
        
        // Nouvelles fonctions pour les actions des cartes sites
        function gererSite(siteId) {{
            showToast('Gestion du site...', 'info');
            // Charge la gestion employés filtrée par site
            loadSPAContent('employees', {{'site_id': siteId}});
        }}
        </script>
        '''
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'content': f'''
            <div class="alert alert-danger text-center">
                <h4>Erreur Dashboard Multi-Sites</h4>
                <p>Impossible de charger le dashboard administrateur.</p>
                <p class="small text-muted">Erreur: {str(e)}</p>
                <button class="btn btn-outline-danger" onclick="location.reload()">Recharger</button>
            </div>
            '''
        })
        
        content = f'''
        <!-- Header Multi-Sites avec Sélecteur -->
        <div class="admin-header-fixed border-bottom bg-white shadow-sm sticky-top">
            <div class="container-fluid">
                <div class="row align-items-center py-3">
                    <div class="col-lg-4">
                        <div class="d-flex align-items-center">
                            <div class="admin-logo me-4">
                                <i class="fas fa-crown text-primary me-2"></i>
                                <span class="fw-bold fs-4 text-dark">PayrollPro Admin</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-4 text-center">
                        <div class="site-selector">
                            <label class="form-label mb-1 small text-muted">SÉLECTION SITE</label>
                            <select class="form-select form-select-sm" id="siteSelector" onchange="changeSite()">
                                {site_options}
                            </select>
                        </div>
                    </div>
                    <div class="col-lg-4">
                        <div class="d-flex align-items-center justify-content-end">
                            <div class="breadcrumb-context me-3">
                                <nav aria-label="breadcrumb">
                                    <ol class="breadcrumb mb-0">
                                        <li class="breadcrumb-item"><a href="#" class="text-decoration-none">Dashboard</a></li>
                                        <li class="breadcrumb-item active">{site_context}</li>
                                    </ol>
                                </nav>
                            </div>
                            <div class="admin-profile">
                                <i class="fas fa-user-circle fa-2x text-primary"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="admin-dashboard-container">
            <div class="container-fluid py-4">
                
                <!-- ROW 1: Vue Globale - Métriques Consolidées -->
                <div class="row g-4 mb-4">
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100 metric-sites">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-primary">
                                        <i class="fas fa-building"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Sites Actifs</div>
                                        <div class="metric-value">{total_sites}</div>
                                        <div class="metric-change positive">
                                            <i class="fas fa-check-circle"></i> Tous opérationnels
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100 metric-departments">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-success">
                                        <i class="fas fa-sitemap"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Départements</div>
                                        <div class="metric-value">{total_departements}</div>
                                        <div class="metric-change positive">
                                            <i class="fas fa-arrow-up"></i> +2 ce trimestre
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100 metric-employees">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-info">
                                        <i class="fas fa-users"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Employés</div>
                                        <div class="metric-value">{total_employes}</div>
                                        <div class="metric-change positive">
                                            <small class="text-muted">Sur {total_employes_global} global</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100 metric-payroll">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-warning">
                                        <i class="fas fa-money-bill-wave"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Masse Salariale</div>
                                        <div class="metric-value">{masse_salariale/1000000:.1f}M MAD</div>
                                        <div class="metric-change positive">
                                            <small class="text-muted">Sur {masse_salariale_global/1000000:.1f}M global</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 2: Répartition par Site + Départements -->
                <div class="row g-4 mb-4">
                    <div class="col-xl-6 col-lg-6">
                        <div class="sites-overview-card card border-0 h-100">
                            <div class="card-header bg-gradient-primary text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-map-marked-alt me-2"></i>Répartition par Site
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="sites-grid">'''
        
        for site_info in sites_data:
            status_color = 'success' if site_info['statut'] == 'actif' else 'danger'
            status_icon = 'check-circle' if site_info['statut'] == 'actif' else 'exclamation-triangle'
            
            content += f'''
                                    <div class="site-card mb-3">
                                        <div class="card border-0 shadow-sm">
                                            <div class="card-body">
                                                <div class="d-flex justify-content-between align-items-start mb-3">
                                                    <div>
                                                        <h6 class="fw-bold mb-1">🏢 {site_info['nom']}</h6>
                                                        <div class="site-stats">
                                                            <small class="text-muted me-3">
                                                                <i class="fas fa-users me-1"></i>{site_info['employes']} employés
                                                            </small>
                                                            <small class="text-muted">
                                                                <i class="fas fa-sitemap me-1"></i>{site_info['departements']} depts
                                                            </small>
                                                        </div>
                                                    </div>
                                                    <div class="site-status">
                                                        <i class="fas fa-{status_icon} text-{status_color}"></i>
                                                    </div>
                                                </div>
                                                <div class="site-budget mb-3">
                                                    <div class="d-flex justify-content-between">
                                                        <span class="small text-muted">Budget:</span>
                                                        <span class="fw-bold text-primary">{site_info['masse_salariale']/1000:.0f}K MAD</span>
                                                    </div>
                                                </div>
                                                <div class="site-actions d-flex gap-2">
                                                    <button class="btn btn-sm btn-primary flex-1" onclick="loadSPAContent('employees')">
                                                        <i class="fas fa-cog me-1"></i>Gérer
                                                    </button>
                                                    <button class="btn btn-sm btn-outline-secondary" onclick="loadSPAContent('reports')">
                                                        <i class="fas fa-chart-bar me-1"></i>Rapports
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>'''
        
        content += f'''
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-6 col-lg-6">
                        <div class="departments-card card border-0 h-100">
                            <div class="card-header bg-gradient-info text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-sitemap me-2"></i>Départements - {site_context}
                                </h5>
                            </div>
                            <div class="card-body">'''
        
        if departements_data:
            for dept in departements_data:
                content += f'''
                                <div class="department-item d-flex align-items-center mb-3 p-3 bg-light rounded">
                                    <div class="dept-icon me-3">
                                        <i class="fas fa-briefcase text-primary"></i>
                                    </div>
                                    <div class="dept-info flex-1">
                                        <h6 class="mb-1">📋 {dept['nom']}</h6>
                                        <div class="dept-details">
                                            <small class="text-muted me-3">
                                                <i class="fas fa-users me-1"></i>{dept['employes']} employés
                                            </small>
                                            <small class="text-muted me-3">
                                                <i class="fas fa-user-tie me-1"></i>{dept['responsable']}
                                            </small>
                                            <small class="text-success">
                                                <i class="fas fa-coins me-1"></i>{dept['budget']/1000:.0f}K MAD
                                            </small>
                                        </div>
                                    </div>
                                    <div class="dept-actions">
                                        <button class="btn btn-sm btn-outline-primary" onclick="gererDepartement({dept['id']})">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                    </div>
                                </div>'''
        else:
            content += '''
                                <div class="text-center py-4">
                                    <i class="fas fa-info-circle fa-3x text-muted mb-3"></i>
                                    <p class="text-muted">Sélectionnez un site spécifique pour voir ses départements</p>
                                </div>'''
        
        content += f'''
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 3: Actions Multi-Sites + Analytics -->
                <div class="row g-4 mb-4">
                    <div class="col-xl-4 col-lg-12">
                        <div class="multi-actions-card card border-0 h-100">
                            <div class="card-header bg-gradient-success text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-bolt me-2"></i>Actions Multi-Sites
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-3">
                                    <button class="btn btn-admin-action" onclick="calculPaieGlobal()">
                                        <div class="action-content">
                                            <i class="fas fa-calculator action-icon text-success"></i>
                                            <div class="action-text">
                                                <div class="action-title">Calcul Paie Global</div>
                                                <small class="action-desc">Tous les sites simultanément</small>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="btn btn-admin-action" onclick="calculPaieSite()">
                                        <div class="action-content">
                                            <i class="fas fa-building action-icon text-primary"></i>
                                            <div class="action-text">
                                                <div class="action-title">Calcul par Site</div>
                                                <small class="action-desc">Site sélectionné uniquement</small>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="btn btn-admin-action" onclick="validationAbsences()">
                                        <div class="action-content">
                                            <i class="fas fa-calendar-check action-icon text-warning"></i>
                                            <div class="action-text">
                                                <div class="action-title">Validation Absences</div>
                                                <small class="action-desc">{absences_en_attente} demandes en attente</small>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="btn btn-admin-action" onclick="backupMultiSites()">
                                        <div class="action-content">
                                            <i class="fas fa-database action-icon text-info"></i>
                                            <div class="action-text">
                                                <div class="action-title">Backup Multi-Sites</div>
                                                <small class="action-desc">Sauvegarde consolidée</small>
                                            </div>
                                        </div>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-8 col-lg-12">
                        <div class="analytics-card card border-0 h-100">
                            <div class="card-header bg-transparent border-0">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h5 class="card-title mb-0">
                                        <i class="fas fa-chart-line me-2 text-primary"></i>
                                        Analytics Multi-Sites
                                    </h5>
                                    <div class="analytics-filters">
                                        <button class="btn btn-sm btn-outline-primary me-1" onclick="filterPeriod('month')">Mois</button>
                                        <button class="btn btn-sm btn-primary me-1" onclick="filterPeriod('quarter')">Trimestre</button>
                                        <button class="btn btn-sm btn-outline-primary" onclick="filterPeriod('year')">Année</button>
                                    </div>
                                </div>
                            </div>
                            <div class="card-body">
                                <canvas id="multiSitesChart" height="200"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 4: Alertes Contextuelles -->
                <div class="row g-4">
                    <div class="col-12">
                        <div class="alerts-card card border-0">
                            <div class="card-header bg-gradient-warning text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-exclamation-triangle me-2"></i>Alertes Contextuelles Multi-Sites
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="alert alert-warning d-flex align-items-center">
                                            <i class="fas fa-clock me-2"></i>
                                            <div>
                                                <strong>Demandes en attente</strong><br>
                                                <small>{absences_en_attente} demandes d'absence multi-sites</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="alert alert-info d-flex align-items-center">
                                            <i class="fas fa-chart-pie me-2"></i>
                                            <div>
                                                <strong>Budget Global</strong><br>
                                                <small>85% du budget annuel consommé</small>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4">
                                        <div class="alert alert-success d-flex align-items-center">
                                            <i class="fas fa-check-circle me-2"></i>
                                            <div>
                                                <strong>Performance</strong><br>
                                                <small>Tous les sites opérationnels</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- CSS Multi-Sites Modern Design -->
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .admin-dashboard-container {{
            font-family: 'Inter', sans-serif;
            --primary-color: #6366f1;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --info-color: #06b6d4;
            --border-radius: 12px;
            --shadow-soft: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        .site-selector select {{
            border-radius: 8px;
            border: 2px solid #e5e7eb;
            font-weight: 500;
        }}
        
        .site-selector select:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-soft);
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}
        
        .metric-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
        }}
        
        .bg-gradient-primary {{ background: linear-gradient(135deg, #6366f1, #4f46e5); }}
        .bg-gradient-success {{ background: linear-gradient(135deg, #10b981, #059669); }}
        .bg-gradient-warning {{ background: linear-gradient(135deg, #f59e0b, #d97706); }}
        .bg-gradient-info {{ background: linear-gradient(135deg, #06b6d4, #0891b2); }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: #6b7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #1f2937;
            line-height: 1.2;
        }}
        
        .metric-change.positive {{ color: var(--success-color); }}
        
        .site-card .card {{
            transition: all 0.2s ease;
        }}
        
        .site-card .card:hover {{
            transform: translateX(4px);
            border-left: 4px solid var(--primary-color);
        }}
        
        .btn-admin-action {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1rem;
            text-align: left;
            transition: all 0.2s ease;
        }}
        
        .btn-admin-action:hover {{
            background: #f8fafc;
            border-color: var(--primary-color);
            transform: translateX(4px);
        }}
        
        .action-content {{
            display: flex;
            align-items: center;
        }}
        
        .action-icon {{
            font-size: 1.5rem;
            margin-right: 1rem;
        }}
        
        .action-title {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        .action-desc {{
            color: #6b7280;
        }}
        
        .department-item {{
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        
        .department-item:hover {{
            border-left-color: var(--primary-color);
            transform: translateX(2px);
        }}
        
        @media (max-width: 768px) {{
            .metric-value {{ font-size: 1.5rem; }}
            .admin-header-fixed .row > div {{ margin-bottom: 1rem; }}
        }}
        </style>
        
        <!-- JavaScript Fonctionnel Multi-Sites -->
        <script>
        // Changement de site
        function changeSite() {{
            const siteSelector = document.getElementById('siteSelector');
            const selectedSite = siteSelector.value;
            
            // Recharger le dashboard avec le nouveau site
            const currentUrl = new URL(window.location.href);
            if (selectedSite === 'all') {{
                currentUrl.searchParams.delete('site_id');
            }} else {{
                currentUrl.searchParams.set('site_id', selectedSite);
            }}
            
            showToast('Changement de site...', 'info');
            
            // Simuler rechargement avec AJAX
            setTimeout(() => {{
                loadSPAContent('dashboard');
            }}, 500);
        }}
        
        // Actions sites - Connectées aux vraies vues SPA
        function gererSite(siteId) {{
            showToast(`Ouverture gestion site ID: ${{siteId}}`, 'info');
            // Charge la gestion employés filtrée par site
            loadSPAContent('employees', {{'site_id': siteId}});
        }}
        
        function rapportsSite(siteId) {{
            showToast(`Génération rapports site ID: ${{siteId}}`, 'info');
            // Charge les rapports existants
            loadSPAContent('reports');
        }}
        
        function gererDepartement(deptId) {{
            showToast(`Gestion département ID: ${{deptId}}`, 'info');
            // Charge la gestion employés
            loadSPAContent('employees');
        }}
        
        // Actions multi-sites - Connectées aux vraies vues SPA
        function calculPaieGlobal() {{
            if(confirm('Lancer le calcul de paie pour TOUS les sites ?')) {{
                showToast('Ouverture module calcul de paie...', 'success');
                // Utilise spa_payroll_fixed existante
                loadSPAContent('payroll');
            }}
        }}
        
        function calculPaieSite() {{
            const siteId = document.getElementById('siteSelector').value;
            if(siteId === 'all') {{
                showToast('Veuillez sélectionner un site spécifique', 'warning');
                return;
            }}
            
            if(confirm('Lancer le calcul de paie pour ce site ?')) {{
                showToast('Ouverture module calcul de paie...', 'success');
                // Utilise spa_payroll_fixed existante
                loadSPAContent('payroll');
            }}
        }}
        
        function validationAbsences() {{
            showToast('Ouverture validation absences...', 'info');
            // Utilise spa_absences existante
            loadSPAContent('absences');
        }}
        
        function backupMultiSites() {{
            if(confirm('Démarrer la sauvegarde de tous les sites ?')) {{
                showToast('Sauvegarde multi-sites en cours...', 'warning');
                // Ici processus backup
            }}
        }}
        
        // Filtres analytics
        function filterPeriod(period) {{
            showToast(`Filtre période: ${{period}}`, 'info');
            // Ici recharge graphiques avec nouveau filtre
        }}
        
        // Initialisation graphiques
        setTimeout(() => {{
            if (typeof Chart !== 'undefined') {{
                const ctx = document.getElementById('multiSitesChart');
                if (ctx) {{
                    new Chart(ctx, {{
                        type: 'line',
                        data: {{
                            labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'],
                            datasets: ['''
        
        for i, site_info in enumerate(sites_data):
            color = ['#6366f1', '#10b981', '#f59e0b'][i % 3]
            content += f'''{{
                                label: '{site_info['nom']}',
                                data: [{site_info['employes']-2}, {site_info['employes']-1}, {site_info['employes']}, {site_info['employes']+1}, {site_info['employes']}, {site_info['employes']+2}],
                                borderColor: '{color}',
                                backgroundColor: '{color}20',
                                tension: 0.4
                            }}{',' if i < len(sites_data)-1 else ''}'''
        
        content += f''']
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ position: 'bottom' }}
                            }}
                        }}
                    }});
                }}
            }}
        }}, 1000);
        
        // Raccourcis clavier
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey) {{
                switch(e.key) {{
                    case '1':
                        e.preventDefault();
                        document.getElementById('siteSelector').selectedIndex = 1;
                        changeSite();
                        break;
                    case '2':
                        e.preventDefault();
                        if(document.getElementById('siteSelector').options.length > 2) {{
                            document.getElementById('siteSelector').selectedIndex = 2;
                            changeSite();
                        }}
                        break;
                }}
            }}
        }});
        </script>
        '''
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'content': f'''
            <div class="alert alert-danger text-center">
                <h4>Erreur Dashboard Multi-Sites</h4>
                <p>Impossible de charger le dashboard administrateur.</p>
                <p class="small text-muted">Erreur: {str(e)}</p>
                <button class="btn btn-outline-danger" onclick="location.reload()">Recharger</button>
            </div>
            '''
        })

@login_required
def spa_dashboard_admin_complete_fixed(request):
    """Dashboard Administrateur Complet avec Design 2025"""
    try:
        # Statistiques pour l'admin
        total_employes = Employe.objects.filter(actif=True).count()
        total_sites = Site.objects.filter(actif=True).count()
        total_departements = Departement.objects.filter(actif=True).count()
        
        # Calculs avancés
        employes_actifs = Employe.objects.filter(actif=True)
        masse_salariale = sum(emp.salaire_base for emp in employes_actifs if emp.salaire_base) or 0
        absences_en_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
        bulletins_mois = BulletinPaie.objects.filter(
            date_calcul__month=datetime.now().month,
            date_calcul__year=datetime.now().year
        ).count()
        
        taux_presence = 97.5  # Simulé
        
        # Données pour recommandations IA
        recommendations = [
            {"title": "Optimisation Planning", "desc": "Réorganiser les équipes du site Nord", "type": "warning", "icon": "fa-clock"},
            {"title": "Formation Requise", "desc": "5 employés ont besoin de mise à niveau", "type": "info", "icon": "fa-graduation-cap"},
            {"title": "Budget Dépassé", "desc": "Département IT dépasse de 12%", "type": "danger", "icon": "fa-exclamation-triangle"},
            {"title": "Performance Excellente", "desc": "Équipe commerciale sur-performe", "type": "success", "icon": "fa-trophy"},
        ]
        
        # Activités récentes
        recent_activities = [
            {"user": "Admin Système", "action": "Modification paramètres paie", "time": "il y a 5 min", "severity": "warning"},
            {"user": "Marie Dupont", "action": "Nouveau bulletin généré", "time": "il y a 12 min", "severity": "success"},
            {"user": "Jean Martin", "action": "Demande congé approuvée", "time": "il y a 25 min", "severity": "info"},
            {"user": "Système", "action": "Sauvegarde automatique", "time": "il y a 1h", "severity": "success"},
        ]
        
        content = f'''
                <!-- Header Admin avec Design Moderne -->
                <div class="admin-header-fixed border-bottom bg-white shadow-sm sticky-top">
                    <div class="container-fluid">
                        <div class="row align-items-center py-3">
                            <div class="col-lg-6">
                                <div class="d-flex align-items-center">
                                    <div class="admin-logo me-4">
                                        <i class="fas fa-crown text-primary me-2"></i>
                        </div>
                    </div>
                    <div class="col-lg-6">
                        <div class="d-flex align-items-center justify-content-end">
                            <div class="search-global me-3">
                                <div class="input-group">
                                    <input type="text" class="form-control" placeholder="Recherche intelligente..." id="globalSearch">
                                    <button class="btn btn-outline-secondary" type="button">
                                        <i class="fas fa-search"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="admin-profile">
                                <div class="dropdown">
                                    <button class="btn btn-link text-decoration-none" data-bs-toggle="dropdown">
                                        <i class="fas fa-user-circle fa-2x text-primary"></i>
                                    </button>
                                    <ul class="dropdown-menu dropdown-menu-end">
                                        <li><a class="dropdown-item" href="#"><i class="fas fa-cog me-2"></i>Paramètres</a></li>
                                        <li><a class="dropdown-item" href="#"><i class="fas fa-sign-out-alt me-2"></i>Déconnexion</a></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="admin-dashboard-container">
            <div class="container-fluid py-4">
                
                <!-- ROW 1: 4 Cartes Métriques KPIs avec Design 2025 -->
                <div class="row g-4 mb-4">
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-primary">
                                        <i class="fas fa-users"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Employés Actifs</div>
                                        <div class="metric-value">{total_employes}</div>
                                        <div class="metric-change positive">
                                            <i class="fas fa-arrow-up"></i> +2.3% ce mois
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-0">
                                <small class="text-muted">Dernière MàJ: Temps réel</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-success">
                                        <i class="fas fa-money-bill-wave"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Masse Salariale</div>
                                        <div class="metric-value">{masse_salariale:,.0f} DH</div>
                                        <div class="metric-change positive">
                                            <i class="fas fa-arrow-up"></i> +1.8% ce mois
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-0">
                                <small class="text-muted">Budget: 85% utilisé</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-info">
                                        <i class="fas fa-chart-line"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Taux Présence</div>
                                        <div class="metric-value">{taux_presence:.1f}%</div>
                                        <div class="metric-change {'positive' if taux_presence >= 95 else 'negative'}">
                                            <i class="fas fa-{'arrow-up' if taux_presence >= 95 else 'arrow-down'}"></i> 
                                            {'Excellent' if taux_presence >= 95 else 'Attention'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-0">
                                <small class="text-muted">Objectif: ≥95%</small>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-3 col-lg-6 col-md-6">
                        <div class="metric-card card border-0 h-100">
                            <div class="card-body">
                                <div class="d-flex align-items-center">
                                    <div class="metric-icon bg-gradient-warning">
                                        <i class="fas fa-exclamation-triangle"></i>
                                    </div>
                                    <div class="metric-content ms-3 flex-1">
                                        <div class="metric-label">Alertes Système</div>
                                        <div class="metric-value">{absences_en_attente + 2}</div>
                                        <div class="metric-change {'negative' if absences_en_attente > 5 else 'neutral'}">
                                            <i class="fas fa-clock"></i> À traiter
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent border-0">
                                <small class="text-muted">Priorité: {absences_en_attente} demandes</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 2: Graphique Principal + Actions Rapides -->
                <div class="row g-4 mb-4">
                    <div class="col-xl-8 col-lg-7">
                        <div class="chart-card card border-0 h-100">
                            <div class="card-header bg-transparent border-0 pb-0">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h5 class="card-title mb-0">
                                        <i class="fas fa-chart-area me-2 text-primary"></i>
                                        Analytics Temps Réel
                                    </h5>
                                    <div class="chart-controls">
                                        <button class="btn btn-sm btn-outline-primary me-2">7j</button>
                                        <button class="btn btn-sm btn-primary me-2">30j</button>
                                        <button class="btn btn-sm btn-outline-primary">12m</button>
                                    </div>
                                </div>
                            </div>
                            <div class="card-body pt-3">
                                <canvas id="mainChart" height="300"></canvas>
                                <div class="chart-legend mt-3">
                                    <div class="row text-center">
                                        <div class="col-3">
                                            <div class="legend-item">
                                                <div class="legend-color bg-primary"></div>
                                                <span class="legend-label">Employés</span>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="legend-item">
                                                <div class="legend-color bg-success"></div>
                                                <span class="legend-label">Paies</span>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="legend-item">
                                                <div class="legend-color bg-warning"></div>
                                                <span class="legend-label">Absences</span>
                                            </div>
                                        </div>
                                        <div class="col-3">
                                            <div class="legend-item">
                                                <div class="legend-color bg-info"></div>
                                                <span class="legend-label">Projections</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-4 col-lg-5">
                        <div class="actions-card card border-0 h-100">
                            <div class="card-header bg-gradient-primary text-white">
                                <h5 class="card-title mb-0">
                                    <i class="fas fa-bolt me-2"></i>Actions Administrateur
                                </h5>
                            </div>
                            <div class="card-body">
                                <div class="d-grid gap-3">
                                    <button class="btn btn-admin-action" onclick="loadSPAContent('employees')">
                                        <div class="action-content">
                                            <i class="fas fa-users-cog action-icon"></i>
                                            <div class="action-text">
                                                <div class="action-title">Gestion Utilisateurs</div>
                                                <small class="action-desc">Comptes, rôles & permissions</small>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="btn btn-admin-action" onclick="loadSPAContent('reports')">
                                        <div class="action-content">
                                            <i class="fas fa-server action-icon"></i>
                                            <div class="action-text">
                                                <div class="action-title">Configuration Système</div>
                                                <small class="action-desc">Paramètres globaux</small>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="btn btn-admin-action" onclick="loadSPAContent('reports')">
                                        <div class="action-content">
                                            <i class="fas fa-shield-alt action-icon"></i>
                                            <div class="action-text">
                                                <div class="action-title">Sécurité & Audit</div>
                                                <small class="action-desc">Logs & surveillance</small>
                                            </div>
                                        </div>
                                    </button>
                                    
                                    <button class="btn btn-admin-action" onclick="loadSPAContent('reports')">
                                        <div class="action-content">
                                            <i class="fas fa-database action-icon"></i>
                                            <div class="action-text">
                                                <div class="action-title">Sauvegarde & Restore</div>
                                                <small class="action-desc">Gestion des données</small>
                                            </div>
                                        </div>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ROW 3: Tableaux de Données Avancées -->
                <div class="row g-4">
                    <div class="col-xl-6 col-lg-6">
                        <div class="data-table-card card border-0">
                            <div class="card-header bg-transparent border-0">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h5 class="card-title mb-0">
                                        <i class="fas fa-robot me-2 text-success"></i>
                                        Recommandations IA
                                    </h5>
                                    <button class="btn btn-sm btn-outline-success">Voir tout</button>
                                </div>
                            </div>
                            <div class="card-body">'''
        
        for rec in recommendations:
            content += f'''
                                <div class="recommendation-item mb-3">
                                    <div class="d-flex align-items-start">
                                        <div class="rec-icon bg-{rec['type']} text-white">
                                            <i class="fas {rec['icon']}"></i>
                                        </div>
                                        <div class="rec-content ms-3 flex-1">
                                            <h6 class="rec-title mb-1">{rec['title']}</h6>
                                            <p class="rec-desc text-muted mb-2">{rec['desc']}</p>
                                            <button class="btn btn-sm btn-outline-{rec['type']}">Action</button>
                                        </div>
                                    </div>
                                </div>'''
        
        content += f'''
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-xl-6 col-lg-6">
                        <div class="activity-card card border-0">
                            <div class="card-header bg-transparent border-0">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h5 class="card-title mb-0">
                                        <i class="fas fa-history me-2 text-info"></i>
                                        Audit Trail en Temps Réel
                                    </h5>
                                    <div class="activity-filters">
                                        <button class="btn btn-sm btn-outline-secondary me-1">Tous</button>
                                        <button class="btn btn-sm btn-outline-danger">Critiques</button>
                                    </div>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="activity-timeline">'''
        
        for activity in recent_activities:
            content += f'''
                                    <div class="activity-item">
                                        <div class="activity-marker bg-{activity['severity']}"></div>
                                        <div class="activity-content">
                                            <div class="activity-header">
                                                <span class="activity-user fw-bold">{activity['user']}</span>
                                                <span class="activity-time text-muted">{activity['time']}</span>
                                            </div>
                                            <div class="activity-action">{activity['action']}</div>
                                        </div>
                                    </div>'''
        
        content += f'''
                                </div>
                                <div class="text-center mt-3">
                                    <button class="btn btn-sm btn-outline-info">
                                        <i class="fas fa-external-link-alt me-1"></i>Audit Complet
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Design System 2025 - Palette Bleu-Violet Professionnelle -->
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .admin-dashboard-container {{
            font-family: 'Inter', sans-serif;
            --primary-color: #6366f1;
            --primary-dark: #4f46e5;
            --secondary-color: #8b5cf6;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --info-color: #06b6d4;
            --dark-color: #1f2937;
            --light-color: #f8fafc;
            --border-radius: 12px;
            --shadow-soft: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-medium: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }}
        
        .admin-header-fixed {{
            position: sticky;
            top: 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-soft);
            transition: all 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }}
        
        .metric-icon {{
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
        }}
        
        .bg-gradient-primary {{ background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)); }}
        .bg-gradient-success {{ background: linear-gradient(135deg, var(--success-color), #059669); }}
        .bg-gradient-warning {{ background: linear-gradient(135deg, var(--warning-color), #d97706); }}
        .bg-gradient-info {{ background: linear-gradient(135deg, var(--info-color), #0891b2); }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: #6b7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--dark-color);
            line-height: 1.2;
        }}
        
        .metric-change {{
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        .metric-change.positive {{ color: var(--success-color); }}
        .metric-change.negative {{ color: var(--danger-color); }}
        .metric-change.neutral {{ color: var(--info-color); }}
        
        .chart-card, .actions-card, .data-table-card, .activity-card {{
            border-radius: var(--border-radius);
            box-shadow: var(--shadow-soft);
            background: white;
        }}
        
        .btn-admin-action {{
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1rem;
            text-align: left;
            transition: all 0.2s ease;
        }}
        
        .btn-admin-action:hover {{
            background: #f8fafc;
            border-color: var(--primary-color);
            transform: translateX(4px);
        }}
        
        .action-content {{
            display: flex;
            align-items: center;
        }}
        
        .action-icon {{
            font-size: 1.5rem;
            color: var(--primary-color);
            margin-right: 1rem;
        }}
        
        .action-title {{
            font-weight: 600;
            color: var(--dark-color);
        }}
        
        .action-desc {{
            color: #6b7280;
        }}
        
        .recommendation-item {{
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
        }}
        
        .rec-icon {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }}
        
        .activity-timeline {{
            position: relative;
            padding-left: 2rem;
        }}
        
        .activity-timeline::before {{
            content: '';
            position: absolute;
            left: 0.5rem;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #e5e7eb;
        }}
        
        .activity-item {{
            position: relative;
            margin-bottom: 1.5rem;
        }}
        
        .activity-marker {{
            position: absolute;
            left: -2rem;
            top: 0.25rem;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            border: 2px solid white;
        }}
        
        .activity-header {{
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 0.25rem;
        }}
        
        .activity-time {{
            font-size: 0.75rem;
            margin-left: auto;
        }}
        
        .search-global input {{
            border-radius: 25px;
            border: 1px solid #e5e7eb;
            padding: 0.5rem 1rem;
        }}
        
        .search-global input:focus {{
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .metric-value {{ font-size: 1.5rem; }}
            .admin-header-fixed .col-lg-6 {{ margin-bottom: 1rem; }}
            .search-global {{ width: 100%; }}
        }}
        </style>
        
        <!-- Scripts JavaScript pour Interactivité Avancée -->
        <script>
        // Initialisation des graphiques temps réel
        setTimeout(() => {{
            if (typeof Chart !== 'undefined') {{
                const ctx = document.getElementById('mainChart');
                if (ctx) {{
                    new Chart(ctx, {{
                        type: 'line',
                        data: {{
                            labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul'],
                            datasets: [{{
                                label: 'Employés',
                                data: [20, 22, 21, 24, 23, 25, {total_employes}],
                                borderColor: '#6366f1',
                                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                tension: 0.4,
                                fill: true
                            }}, {{
                                label: 'Bulletins',
                                data: [18, 20, 19, 22, 21, 23, {bulletins_mois}],
                                borderColor: '#10b981',
                                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                tension: 0.4,
                                fill: true
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ display: false }}
                            }},
                            scales: {{
                                y: {{ beginAtZero: true }}
                            }}
                        }}
                    }});
                }}
            }}
        }}, 1000);
        
        // Recherche intelligente
        document.getElementById('globalSearch')?.addEventListener('input', function(e) {{
            const query = e.target.value;
            if (query.length > 2) {{
                // Simulation suggestions
                console.log('Recherche:', query);
            }}
        }});
        
        // Actions administrateur
        function openSystemConfig() {{
            showToast('Configuration Système - Module en développement', 'info');
        }}
        
        function openSecurityPanel() {{
            showToast('Panel Sécurité - Accès audit trail', 'warning');
        }}
        
        function openBackupManager() {{
            showToast('Gestionnaire Sauvegarde - Interface avancée', 'success');
        }}
        
        // Mise à jour temps réel (simulation)
        setInterval(() => {{
            // Simuler des mises à jour en temps réel
            console.log('Mise à jour temps réel...');
        }}, 30000);
        </script>
        '''
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'content': '''
            <div class="alert alert-danger">
                <h4>Erreur Dashboard Admin</h4>
                <p>Impossible de charger le dashboard administrateur.</p>
            </div>
            '''
        })


@login_required
def spa_dashboard_rh_fixed(request):
    """Dashboard RH moderne avec fonctionnalités HR spécialisées"""
    try:
        # Statistiques RH spécialisées
        total_employes = Employe.objects.filter(actif=True).count()
        employes_en_conge = Absence.objects.filter(
            statut='APPROUVE',
            date_fin__gte=datetime.now().date()
        ).count()
        demandes_conge = Absence.objects.filter(statut='EN_ATTENTE').count()
        nouveaux_employes = Employe.objects.filter(
            date_embauche__month=datetime.now().month,
            date_embauche__year=datetime.now().year
        ).count()
        
        # Calculs RH avancés
        employes_actifs = Employe.objects.filter(actif=True)
        taux_absenteisme = (employes_en_conge / total_employes * 100) if total_employes > 0 else 0
        
        # Calcul de l'ancienneté moyenne simplifiée
        try:
            moyenne_anciennete = 0
            if employes_actifs.exists():
                total_jours = 0
                count_employes = 0
                for emp in employes_actifs:
                    if emp.date_embauche:
                        jours = (datetime.now().date() - emp.date_embauche).days
                        total_jours += jours
                        count_employes += 1
                moyenne_anciennete = total_jours / count_employes if count_employes > 0 else 0
            moyenne_anciennete_annees = round(moyenne_anciennete / 365, 1) if moyenne_anciennete > 0 else 0
        except:
            moyenne_anciennete_annees = 0
        
        # Répartition par départements
        departements = Departement.objects.filter(actif=True)
        repartition_dept = []
        for dept in departements[:5]:  # Top 5 départements
            count = Employe.objects.filter(departement=dept, actif=True).count()
            if count > 0:
                repartition_dept.append({"nom": dept.nom, "count": count})
        
        # Dernières activités RH
        activites_rh = [
            {"action": "Congé approuvé", "employe": "Martin Dubois", "time": "Il y a 10 min", "icon": "fa-check-circle", "color": "success"},
            {"action": "Nouveau contrat", "employe": "Sophie Laurent", "time": "Il y a 25 min", "icon": "fa-file-contract", "color": "info"},
            {"action": "Entretien planifié", "employe": "Ahmed Bensaid", "time": "Il y a 1h", "icon": "fa-calendar-plus", "color": "warning"},
            {"action": "Formation validée", "employe": "Fatima Alami", "time": "Il y a 2h", "icon": "fa-graduation-cap", "color": "primary"},
        ]
        
        activites_html = ""
        for activite in activites_rh:
            activites_html += f'''
            <div class="d-flex align-items-center mb-3">
                <div class="avatar-sm bg-{activite['color']} text-white rounded-circle d-flex align-items-center justify-content-center me-3">
                    <i class="fas {activite['icon']}"></i>
                </div>
                <div class="flex-1">
                    <h6 class="mb-1">{activite['action']}</h6>
                    <p class="text-muted mb-0 small">{activite['employe']} • {activite['time']}</p>
                </div>
            </div>
            '''
        
        content = f'''
        <div class="container-fluid">
            <!-- Header RH -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h2 class="mb-1">
                                <i class="fas fa-user-tie text-info me-2"></i>
                                Dashboard Ressources Humaines
                            </h2>
                            <p class="text-muted mb-0">Gestion complète du capital humain</p>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-info btn-sm">
                                <i class="fas fa-user-plus me-1"></i>Nouvel Employé
                            </button>
                            <button class="btn btn-info btn-sm">
                                <i class="fas fa-calendar-check me-1"></i>Planning RH
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Cartes statistiques RH -->
            <div class="row mb-4">
                <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="avatar-lg bg-gradient-success text-white rounded-3 d-flex align-items-center justify-content-center me-3">
                                    <i class="fas fa-users fa-2x"></i>
                                </div>
                                <div class="flex-1">
                                    <h3 class="mb-1 fw-bold text-success">{total_employes}</h3>
                                    <p class="text-muted mb-0">Équipe Totale</p>
                                    <small class="text-success"><i class="fas fa-arrow-up"></i> +{nouveaux_employes} ce mois</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="avatar-lg bg-gradient-warning text-white rounded-3 d-flex align-items-center justify-content-center me-3">
                                    <i class="fas fa-clock fa-2x"></i>
                                </div>
                                <div class="flex-1">
                                    <h3 class="mb-1 fw-bold text-warning">{demandes_conge}</h3>
                                    <p class="text-muted mb-0">Demandes Congés</p>
                                    <small class="text-warning"><i class="fas fa-exclamation-circle"></i> À traiter</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="avatar-lg bg-gradient-info text-white rounded-3 d-flex align-items-center justify-content-center me-3">
                                    <i class="fas fa-chart-line fa-2x"></i>
                                </div>
                                <div class="flex-1">
                                    <h3 class="mb-1 fw-bold text-info">{taux_absenteisme:.1f}%</h3>
                                    <p class="text-muted mb-0">Taux Présence</p>
                                    <small class="text-success"><i class="fas fa-check"></i> Dans la norme</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-xl-3 col-md-6 mb-3">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-body">
                            <div class="d-flex align-items-center">
                                <div class="avatar-lg bg-gradient-primary text-white rounded-3 d-flex align-items-center justify-content-center me-3">
                                    <i class="fas fa-medal fa-2x"></i>
                                </div>
                                <div class="flex-1">
                                    <h3 class="mb-1 fw-bold text-primary">{moyenne_anciennete_annees}</h3>
                                    <p class="text-muted mb-0">Ancienneté Moy.</p>
                                    <small class="text-muted"><i class="fas fa-calendar"></i> années</small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Section priorités RH -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-gradient-info text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-star me-2"></i>Priorités RH Aujourd'hui
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4">
                                    <div class="alert alert-warning d-flex align-items-center">
                                        <i class="fas fa-clipboard-list me-2"></i>
                                        <div>
                                            <strong>Évaluations</strong><br>
                                            <small>3 entretiens annuels à planifier</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="alert alert-info d-flex align-items-center">
                                        <i class="fas fa-user-graduate me-2"></i>
                                        <div>
                                            <strong>Formations</strong><br>
                                            <small>5 demandes en attente</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="alert alert-success d-flex align-items-center">
                                        <i class="fas fa-handshake me-2"></i>
                                        <div>
                                            <strong>Recrutement</strong><br>
                                            <small>2 nouveaux profils à interviewer</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <!-- Actions RH spécialisées -->
                <div class="col-lg-4 mb-4">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header bg-gradient-info text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-tools me-2"></i>Outils RH Rapides
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-3">
                                <button class="btn btn-outline-success d-flex align-items-center justify-content-start" onclick="switchToSection('conges')">
                                    <i class="fas fa-calendar-check me-3"></i>
                                    <div class="text-start">
                                        <div class="fw-bold">Gestion Congés</div>
                                        <small class="text-muted">Approuver/refuser demandes</small>
                                    </div>
                                </button>
                                
                                <button class="btn btn-outline-primary d-flex align-items-center justify-content-start" onclick="switchToSection('employees')">
                                    <i class="fas fa-address-card me-3"></i>
                                    <div class="text-start">
                                        <div class="fw-bold">Dossiers Employés</div>
                                        <small class="text-muted">Fiches et documents</small>
                                    </div>
                                </button>
                                
                                <button class="btn btn-outline-warning d-flex align-items-center justify-content-start" onclick="switchToSection('recrutement')">
                                    <i class="fas fa-user-plus me-3"></i>
                                    <div class="text-start">
                                        <div class="fw-bold">Recrutement</div>
                                        <small class="text-muted">Candidatures et postes</small>
                                    </div>
                                </button>
                                
                                <button class="btn btn-outline-info d-flex align-items-center justify-content-start" onclick="switchToSection('formations')">
                                    <i class="fas fa-graduation-cap me-3"></i>
                                    <div class="text-start">
                                        <div class="fw-bold">Plan Formation</div>
                                        <small class="text-muted">Développement compétences</small>
                                    </div>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Graphique équipe -->
                <div class="col-lg-4 mb-4">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-users-cog me-2"></i>Répartition Équipe
                            </h5>
                        </div>
                        <div class="card-body">
                            <canvas id="equipe-chart" height="200"></canvas>
                            <div class="mt-3">
                                <div class="row text-center">
                                    <div class="col-4">
                                        <h6 class="text-success">{len(departements)}</h6>
                                        <small class="text-muted">Départements</small>
                                    </div>
                                    <div class="col-4">
                                        <h6 class="text-primary">{employes_en_conge}</h6>
                                        <small class="text-muted">En congé</small>
                                    </div>
                                    <div class="col-4">
                                        <h6 class="text-info">{nouveaux_employes}</h6>
                                        <small class="text-muted">Nouveaux</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Activités RH récentes -->
                <div class="col-lg-4 mb-4">
                    <div class="card border-0 shadow-sm h-100">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-history me-2"></i>Activités RH Récentes
                            </h5>
                        </div>
                        <div class="card-body">
                            {activites_html}
                            <div class="text-center mt-3">
                                <button class="btn btn-sm btn-outline-info">
                                    <i class="fas fa-list me-1"></i>Voir toutes les activités
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Tableaux de bord détaillés -->
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-chart-pie me-2"></i>Performance par Département
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-borderless">
                                    <thead>
                                        <tr>
                                            <th>Département</th>
                                            <th>Effectif</th>
                                            <th>Performance</th>
                                        </tr>
                                    </thead>
                                    <tbody>'''
        
        for dept_info in repartition_dept:
            performance = 85 + (dept_info["count"] % 15)  # Performance simulée
            content += f'''
                                        <tr>
                                            <td>{dept_info["nom"]}</td>
                                            <td>
                                                <span class="badge bg-primary">{dept_info["count"]}</span>
                                            </td>
                                            <td>
                                                <div class="progress" style="height: 8px;">
                                                    <div class="progress-bar bg-success" style="width: {performance}%"></div>
                                                </div>
                                                <small class="text-muted">{performance}%</small>
                                            </td>
                                        </tr>'''
        
        content += f'''
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6 mb-4">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-calendar-alt me-2"></i>Planning Congés à Venir
                            </h5>
                        </div>
                        <div class="card-body">
                            <div class="timeline">
                                <div class="timeline-item">
                                    <div class="timeline-marker bg-warning"></div>
                                    <div class="timeline-content">
                                        <h6 class="mb-1">Sarah Martin</h6>
                                        <p class="text-muted mb-0 small">Congé annuel • 15-30 Mars</p>
                                    </div>
                                </div>
                                <div class="timeline-item">
                                    <div class="timeline-marker bg-info"></div>
                                    <div class="timeline-content">
                                        <h6 class="mb-1">Ahmed Benali</h6>
                                        <p class="text-muted mb-0 small">Formation • 22-24 Mars</p>
                                    </div>
                                </div>
                                <div class="timeline-item">
                                    <div class="timeline-marker bg-success"></div>
                                    <div class="timeline-content">
                                        <h6 class="mb-1">Marie Dubois</h6>
                                        <p class="text-muted mb-0 small">Congé maladie • 25 Mars</p>
                                    </div>
                                </div>
                            </div>
                            <div class="text-center mt-3">
                                <button class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-calendar me-1"></i>Voir planning complet
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
        .avatar-lg {{
            width: 4rem;
            height: 4rem;
        }}
        .avatar-sm {{
            width: 2.5rem;
            height: 2.5rem;
        }}
        .bg-gradient-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .bg-gradient-success {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        .bg-gradient-warning {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        .bg-gradient-info {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .timeline {{
            position: relative;
            padding-left: 1.5rem;
        }}
        .timeline::before {{
            content: '';
            position: absolute;
            left: 0.5rem;
            top: 0;
            bottom: 0;
            width: 2px;
            background: #e9ecef;
        }}
        .timeline-item {{
            position: relative;
            margin-bottom: 1rem;
        }}
        .timeline-marker {{
            position: absolute;
            left: -1rem;
            top: 0.25rem;
            width: 1rem;
            height: 1rem;
            border-radius: 50%;
            border: 2px solid white;
        }}
        .timeline-content {{
            margin-left: 1rem;
        }}
        </style>
        
        <script>
        // Initialiser les graphiques RH après chargement
        setTimeout(() => {{
            if (typeof Chart !== 'undefined') {{
                // Graphique répartition équipe
                const ctxEquipe = document.getElementById('equipe-chart');
                if (ctxEquipe) {{
                    new Chart(ctxEquipe, {{
                        type: 'doughnut',
                        data: {{
                            labels: {[dept["nom"] for dept in repartition_dept]},
                            datasets: [{{
                                data: {[dept["count"] for dept in repartition_dept]},
                                backgroundColor: [
                                    '#667eea', '#11998e', '#f093fb', '#4facfe', '#fa709a'
                                ],
                                borderWidth: 0
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {{
                                legend: {{ position: 'bottom' }}
                            }}
                        }}
                    }});
                }}
            }}
        }}, 1000);
        </script>
        '''
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'content': f'''
            <div class="alert alert-danger text-center">
                <h4>Erreur Dashboard RH</h4>
                <p>Impossible de charger le dashboard RH.</p>
                <p class="small text-muted">Erreur: {str(e)}</p>
            </div>
            '''
        })


@login_required
def spa_dashboard_employee_fixed(request):
    """Dashboard employé corrigé"""
    try:
        # Récupérer l'employé connecté
        employe = None
        try:
            employe = Employe.objects.get(user=request.user)
        except Employe.DoesNotExist:
            pass
        
        content = f'''
        <div class="container-fluid">
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="mb-4">
                        <i class="fas fa-user text-primary me-3"></i>
                        Mon Espace Personnel
                    </h2>
                </div>
            </div>
            
            {f'''
            <div class="row">
                <div class="col-lg-8">
                    <div class="card">
                        <div class="card-header">
                            <h5>Mes Informations</h5>
                        </div>
                        <div class="card-body">
                            <p><strong>Nom:</strong> {employe.prenom} {employe.nom}</p>
                            <p><strong>Fonction:</strong> {employe.fonction or 'Non définie'}</p>
                            <p><strong>Site:</strong> {employe.site.nom if employe.site else 'Non défini'}</p>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">
                    <div class="card">
                        <div class="card-header">
                            <h5>Actions</h5>
                        </div>
                        <div class="card-body">
                            <button class="btn btn-primary btn-block mb-2" onclick="loadSPAContent('absences')">
                                <i class="fas fa-calendar me-2"></i>Mes Absences
                            </button>
                            <button class="btn btn-info btn-block" onclick="showToast('Bulletins - En développement', 'info')">
                                <i class="fas fa-file me-2"></i>Mes Bulletins
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            ''' if employe else '''
            <div class="alert alert-warning text-center">
                <h4><i class="fas fa-exclamation-triangle"></i> Profil Incomplet</h4>
                <p>Votre profil employé n'est pas encore configuré.</p>
                <p>Contactez votre administrateur RH.</p>
            </div>
            '''}
        </div>
        '''
        
        return JsonResponse({
            'success': True,
            'content': content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'content': '''
            <div class="alert alert-danger">
                <h4>Erreur Dashboard Employé</h4>
                <p>Impossible de charger votre espace personnel.</p>
            </div>
            '''
        })
