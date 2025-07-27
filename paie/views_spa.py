from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from .models import Employe, Absence, BulletinPaie, Site, Departement
from datetime import datetime, timedelta
import json

@login_required
def spa_dashboard(request):
    """Contenu du dashboard principal pour SPA - redirige selon le rôle"""
    if request.user.is_superuser:
        return spa_dashboard_admin(request)
    elif request.user.groups.filter(name='RH').exists():
        return spa_dashboard_rh(request)
    else:
        return spa_dashboard_employee(request)

@login_required
def spa_dashboard_employee(request):
    """Contenu du dashboard employé pour SPA"""
    try:
        # Informations de l'employé connecté
        try:
            employe = Employe.objects.get(user=request.user)
        except Employe.DoesNotExist:
            employe = None
            
        # Absences de l'employé
        mes_absences = Absence.objects.filter(employe=employe).order_by('-date_debut')[:5] if employe else []
        
        # Bulletins de paie récents
        mes_bulletins = BulletinPaie.objects.filter(employe=employe).order_by('-periode')[:3] if employe else []
        
        data = {
            'success': True,
            'content': """
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient mb-4">
                        <i class="fas fa-user me-3"></i>Mon Espace Employé
                    </h2>
                </div>
            </div>
            
            <!-- Informations personnelles -->
            <div class="row mb-4">
                <div class="col-lg-8">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5><i class="fas fa-id-card me-2"></i>Mes Informations</h5>
                        </div>
                        <div class="card-body">""" + 
                        ('<div class="alert alert-warning">Profil employé non configuré. Contactez votre RH.</div>' if not employe else f"""
                            <div class="row">
                                <div class="col-md-6">
                                    <p><strong>Nom :</strong> {employe.nom} {employe.prenom}</p>
                                    <p><strong>Matricule :</strong> {employe.matricule}</p>
                                    <p><strong>Email :</strong> {employe.email}</p>
                                </div>
                                <div class="col-md-6">
                                    <p><strong>Poste :</strong> {employe.poste}</p>
                                    <p><strong>Date d'embauche :</strong> {employe.date_embauche.strftime('%d/%m/%Y')}</p>
                                    <p><strong>Statut :</strong> <span class="badge bg-success">Actif</span></p>
                                </div>
                            </div>
                            """) + """
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5><i class="fas fa-calendar me-2"></i>Mes Statistiques</h5>
                        </div>
                        <div class="card-body text-center">
                            <div class="stats-item mb-3">
                                <div class="stats-number text-primary">""" + str(len(mes_absences)) + """</div>
                                <div class="stats-label">Demandes d'absence</div>
                            </div>
                            <div class="stats-item">
                                <div class="stats-number text-success">""" + str(len(mes_bulletins)) + """</div>
                                <div class="stats-label">Bulletins de paie</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Actions rapides -->
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5><i class="fas fa-bolt me-2"></i>Actions Rapides</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <a href="#" data-spa-section="absences" class="btn btn-outline-primary w-100">
                                        <i class="fas fa-calendar-plus me-2"></i>Demander une absence
                                    </a>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <a href="#" data-spa-section="payroll" class="btn btn-outline-success w-100">
                                        <i class="fas fa-file-invoice me-2"></i>Mes bulletins de paie
                                    </a>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <a href="/paie/profil/" class="btn btn-outline-info w-100">
                                        <i class="fas fa-user-edit me-2"></i>Modifier mon profil
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """
        }
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement du dashboard employé: {str(e)}'
        })

@login_required
def spa_dashboard_admin(request):
    """Contenu du dashboard admin pour SPA"""
    try:
        # Statistiques pour le dashboard admin
        total_employes = Employe.objects.filter(actif=True).count()
        total_bulletins = BulletinPaie.objects.count()
        absences_en_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
        
        # Masse salariale
        employes_actifs = Employe.objects.filter(actif=True)
        masse_salariale = sum(emp.salaire_base for emp in employes_actifs)
        
        # Nouveaux employés ce mois
        debut_mois = datetime.now().replace(day=1)
        nouveaux_employes = Employe.objects.filter(
            date_embauche__gte=debut_mois,
            actif=True
        ).count()
        
        # Sites et départements
        total_sites = Site.objects.count()
        total_departements = Departement.objects.count()
        
        data = {
            'success': True,
            'content': f'''
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient mb-4">
                        <i class="fas fa-tachometer-alt me-3"></i>Dashboard Administrateur
                    </h2>
                </div>
            </div>
            
            <!-- Statistiques principales -->
            <div class="row mb-4">
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{total_employes}</div>
                                <div class="stats-label">Employés Actifs</div>
                            </div>
                            <div class="icon-wrapper">
                                <i class="fas fa-users"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift" style="animation-delay: 0.1s;">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{total_bulletins}</div>
                                <div class="stats-label">Bulletins Générés</div>
                            </div>
                            <div class="icon-wrapper" style="background: var(--success-gradient);">
                                <i class="fas fa-file-invoice"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift" style="animation-delay: 0.2s;">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{absences_en_attente}</div>
                                <div class="stats-label">Absences à Valider</div>
                            </div>
                            <div class="icon-wrapper" style="background: var(--warning-gradient);">
                                <i class="fas fa-calendar-times"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift" style="animation-delay: 0.3s;">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{masse_salariale:,.0f} DH</div>
                                <div class="stats-label">Masse Salariale</div>
                            </div>
                            <div class="icon-wrapper" style="background: var(--primary-gradient);">
                                <i class="fas fa-money-bill-wave"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Actions rapides -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card slide-in-up" style="animation-delay: 0.4s;">
                        <div class="card-header">
                            <h4><i class="fas fa-bolt me-2"></i>Actions Rapides</h4>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-lg-3 col-md-6 mb-3">
                                    <button class="btn btn-modern w-100 hover-scale" onclick="PayrollPro.navigate('/employes/')">
                                        <i class="fas fa-user-plus me-2"></i>Ajouter Employé
                                    </button>
                                </div>
                                <div class="col-lg-3 col-md-6 mb-3">
                                    <button class="btn btn-modern w-100 hover-scale" onclick="PayrollPro.navigate('/calcul-paie/')">
                                        <i class="fas fa-calculator me-2"></i>Calculer Paie
                                    </button>
                                </div>
                                <div class="col-lg-3 col-md-6 mb-3">
                                    <button class="btn btn-modern w-100 hover-scale" onclick="PayrollPro.navigate('/export/excel/')">
                                        <i class="fas fa-file-excel me-2"></i>Export Excel
                                    </button>
                                </div>
                                <div class="col-lg-3 col-md-6 mb-3">
                                    <button class="btn btn-modern w-100 hover-scale" onclick="PayrollPro.navigate('/admin/')">
                                        <i class="fas fa-cogs me-2"></i>Administration
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Informations système -->
            <div class="row">
                <div class="col-lg-6 mb-3">
                    <div class="card slide-in-up" style="animation-delay: 0.5s;">
                        <div class="card-header">
                            <h5><i class="fas fa-building me-2"></i>Structure Organisationnelle</h5>
                        </div>
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-6">
                                    <div class="stats-number">{total_sites}</div>
                                    <div class="stats-label">Sites</div>
                                </div>
                                <div class="col-6">
                                    <div class="stats-number">{total_departements}</div>
                                    <div class="stats-label">Départements</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6 mb-3">
                    <div class="card slide-in-up" style="animation-delay: 0.6s;">
                        <div class="card-header">
                            <h5><i class="fas fa-chart-line me-2"></i>Activité Récente</h5>
                        </div>
                        <div class="card-body">
                            <div class="alert alert-success">
                                <i class="fas fa-check-circle me-2"></i>
                                <strong>{nouveaux_employes}</strong> nouveaux employés ce mois
                            </div>
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                Système opérationnel et à jour
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement du dashboard: {str(e)}'
        })

@login_required
def spa_dashboard_rh(request):
    """Contenu du dashboard RH pour SPA"""
    try:
        # Statistiques RH
        employes_par_departement = Employe.objects.values('departement__nom').annotate(count=Count('id'))
        absences_par_type = Absence.objects.values('type_absence').annotate(count=Count('id'))
        
        # Données pour les graphiques
        chart_labels_dept = [d['departement__nom'] for d in employes_par_departement]
        chart_data_dept = [d['count'] for d in employes_par_departement]
        
        chart_labels_abs = [a['type_absence'] for a in absences_par_type]
        chart_data_abs = [a['count'] for a in absences_par_type]
        
        data = {
            'success': True,
            'content': f'''
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient mb-4">
                        <i class="fas fa-user-tie me-3"></i>Dashboard RH
                    </h2>
                </div>
            </div>
            
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card shadow-sm slide-in-up">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-chart-pie me-2"></i>Employés par Département
                            </h5>
                        </div>
                        <div class="card-body">
                            <canvas id="rhDeptChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="card shadow-sm slide-in-up" style="animation-delay: 0.2s;">
                        <div class="card-header">
                            <h5 class="mb-0">
                                <i class="fas fa-chart-bar me-2"></i>Types d'Absences
                            </h5>
                        </div>
                        <div class="card-body">
                            <canvas id="rhAbsenceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Chart.js pour le dashboard RH
                if (window.rhDeptChart instanceof Chart) {{
                    window.rhDeptChart.destroy();
                }}
                const ctxDept = document.getElementById('rhDeptChart').getContext('2d');
                window.rhDeptChart = new Chart(ctxDept, {{
                    type: 'doughnut',
                    data: {{
                        labels: {json.dumps(chart_labels_dept)},
                        datasets: [{{
                            label: 'Employés',
                            data: {json.dumps(chart_data_dept)},
                            backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'],
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'bottom',
                            }}
                        }}
                    }}
                }});

                if (window.rhAbsenceChart instanceof Chart) {{
                    window.rhAbsenceChart.destroy();
                }}
                const ctxAbs = document.getElementById('rhAbsenceChart').getContext('2d');
                window.rhAbsenceChart = new Chart(ctxAbs, {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(chart_labels_abs)},
                        datasets: [{{
                            label: 'Nombre de jours',
                            data: {json.dumps(chart_data_abs)},
                            backgroundColor: '#4e73df',
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            y: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }};
            </script>
            '''
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({{'success': False, 'error': str(e)}})

@login_required
def spa_employees(request):
    """Contenu de la gestion des employés pour SPA - Version complète et fonctionnelle"""
    try:
        # Récupérer les employés avec leurs relations
        employes = Employe.objects.select_related('site', 'departement', 'user').order_by('nom', 'prenom')
        
        # Récupérer les sites et départements pour les filtres
        sites = Site.objects.all()
        departements = Departement.objects.all()
        
        # Construire le HTML des employés
        employes_html = ""
        for employe in employes:
            status_badge = "success" if employe.actif else "secondary"
            status_text = "Actif" if employe.actif else "Inactif"
            
            employes_html += f'''
            <tr class="employee-row" data-site="{employe.site_id or ''}" data-dept="{employe.departement_id or ''}">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-circle bg-primary text-white d-flex align-items-center justify-content-center me-2">
                            {employe.nom[0]}{employe.prenom[0]}
                        </div>
                        <div>
                            <strong>{employe.nom} {employe.prenom}</strong>
                            <br><small class="text-muted">#{employe.matricule}</small>
                        </div>
                    </div>
                </td>
                <td>{employe.fonction or 'Non défini'}</td>
                <td><span class="text-success fw-bold">{float(employe.salaire_base):,.0f} DH</span></td>
                <td>{employe.site.nom if employe.site else 'Non assigné'}</td>
                <td>{employe.departement.nom if employe.departement else 'Non assigné'}</td>
                <td><span class="badge bg-{status_badge}">{status_text}</span></td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-info btn-action" onclick="viewEmployeeDetails({employe.id})" title="Voir détails">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-warning btn-action" onclick="editEmployeeForm({employe.id})" title="Modifier">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="deactivateEmployee({employe.id}, '{employe.nom} {employe.prenom}')" title="Désactiver">
                            <i class="fas fa-user-times"></i>
                        </button>
                    </div>
                </td>
            </tr>
            '''

        # HTML complet de la page employés avec filtres en haut
        html_content = f'''
        <div class="employees-management-page">
            <!-- En-tête avec titre -->
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient d-flex align-items-center">
                        <i class="fas fa-users text-primary me-3"></i>
                        Gestion des Employés
                        <span class="badge bg-info ms-3">{employes.count()} employé(s)</span>
                    </h2>
                </div>
            </div>
            
            <!-- Section Filtres et Actions en haut -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h5 class="mb-0"><i class="fas fa-filter me-2"></i>Filtres et Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="row g-3 align-items-end">
                                <!-- Filtres -->
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Rechercher</label>
                                    <input type="text" id="searchInput" class="form-control" 
                                           placeholder="Nom, prénom, matricule..." 
                                           onkeyup="filterEmployees()">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Site</label>
                                    <select id="siteFilter" class="form-select" onchange="filterEmployees()">
                                        <option value="">Tous les sites</option>
                                        {"".join([f'<option value="{site.id}">{site.nom}</option>' for site in sites])}
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Département</label>
                                    <select id="deptFilter" class="form-select" onchange="filterEmployees()">
                                        <option value="">Tous les départements</option>
                                        {"".join([f'<option value="{dept.id}">{dept.nom}</option>' for dept in departements])}
                                    </select>
                                </div>
                                <!-- Actions -->
                                <div class="col-md-3">
                                    <div class="d-grid gap-2">
                                        <button class="btn btn-success" onclick="addNewEmployee()">
                                            <i class="fas fa-plus me-2"></i>Ajouter Employé
                                        </button>
                                        <button class="btn btn-primary" onclick="exportToExcel()">
                                            <i class="fas fa-download me-2"></i>Export Excel
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-12">
                                    <button class="btn btn-outline-secondary btn-sm" onclick="clearAllFilters()">
                                        <i class="fas fa-times me-1"></i>Effacer les filtres
                                    </button>
                                    <span id="filterResults" class="ms-3 text-muted"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Section Liste des Employés -->
            <div class="row">
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">
                                <i class="fas fa-list me-2"></i>Liste des Employés
                                <span id="employeeCount" class="badge bg-secondary ms-2">{employes.count()}</span>
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0" id="employeesTable">
                                    <thead class="table-light">
                                        <tr>
                                            <th width="250">Employé</th>
                                            <th>Fonction</th>
                                            <th>Salaire</th>
                                            <th>Site</th>
                                            <th>Département</th>
                                            <th>Statut</th>
                                            <th width="150">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="employeesTableBody">
                                        {employes_html}
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- Message si aucun résultat -->
                            <div id="noResults" class="text-center py-5" style="display: none;">
                                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                                <h5 class="text-muted">Aucun employé trouvé</h5>
                                <p class="text-muted">Essayez de modifier vos critères de recherche</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal pour Employé -->
        <div class="modal fade" id="employeeModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="employeeModalTitle">Gestion Employé</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="employeeModalBody">
                        <!-- Contenu dynamique chargé ici -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal Détails Employé -->
        <div class="modal fade" id="employeeDetailsModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Détails de l'Employé</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="employeeDetailsModalBody">
                        <!-- Contenu dynamique chargé ici -->
                    </div>
                </div>
            </div>
        </div>

        <style>
        .employees-management-page {{
            padding: 0;
        }}
        .avatar-circle {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 14px;
            font-weight: bold;
        }}
        .employee-row:hover {{
            background-color: #f8f9fa;
        }}
        .btn-action {{
            padding: 0.25rem 0.5rem;
            font-size: 0.875rem;
        }}
        .text-gradient {{
            background: linear-gradient(45deg, #007bff, #6610f2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .card {{
            border-radius: 12px;
        }}
        .form-control:focus, .form-select:focus {{
            border-color: #007bff;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        }}
        </style>

        <script>
        console.log('📋 Script SPA Employés chargé');

        // Variables globales
        let allEmployees = [];

        // ===== FONCTIONS PRINCIPALES =====

        // Ajouter un nouvel employé
        function addNewEmployee() {{
            console.log('🆕 Ajout d\\'un nouvel employé');
            
            fetch('/creer_employe/', {{
                method: 'GET',
                headers: {{
                    'X-Requested-With': 'XMLHttpRequest',
                }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    document.getElementById('employeeModalTitle').textContent = 'Ajouter un Nouvel Employé';
                    document.getElementById('employeeModalBody').innerHTML = data.form_html;
                    showModal('employeeModal');
                    showSuccess('Formulaire d\\'ajout chargé');
                }} else {{
                    showError('Erreur: ' + (data.error || 'Impossible de charger le formulaire'));
                }}
            }})
            .catch(error => {{
                showError('Erreur de connexion: ' + error.message);
            }});
        }}

        // Modifier un employé
        function editEmployeeForm(employeeId) {{
            console.log('✏️ Modification employé ID:', employeeId);
            
            fetch(`/modifier_employe/${{employeeId}}/`, {{
                method: 'GET',
                headers: {{
                    'X-Requested-With': 'XMLHttpRequest',
                }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    document.getElementById('employeeModalTitle').textContent = 'Modifier l\\'Employé';
                    document.getElementById('employeeModalBody').innerHTML = data.form_html;
                    showModal('employeeModal');
                    showSuccess('Formulaire de modification chargé');
                }} else {{
                    showError('Erreur: ' + (data.error || 'Employé non trouvé'));
                }}
            }})
            .catch(error => {{
                showError('Erreur de connexion: ' + error.message);
            }});
        }}

        // Voir détails d'un employé
        function viewEmployeeDetails(employeeId) {{
            console.log('👁️ Affichage détails employé ID:', employeeId);
            
            fetch(`/detail_employe/${{employeeId}}/`, {{
                headers: {{
                    'X-Requested-With': 'XMLHttpRequest',
                }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    displayEmployeeDetails(data);
                    showModal('employeeDetailsModal');
                }} else {{
                    showError('Erreur: ' + (data.error || 'Impossible de charger les détails'));
                }}
            }})
            .catch(error => {{
                showError('Erreur de connexion: ' + error.message);
            }});
        }}

        // Désactiver un employé
        function deactivateEmployee(employeeId, employeeName) {{
            if (!confirm(`Êtes-vous sûr de vouloir désactiver l'employé ${{employeeName}} ?`)) {{
                return;
            }}

            console.log('🗑️ Désactivation employé ID:', employeeId);
            
            fetch(`/api/delete_employe/${{employeeId}}/`, {{
                method: 'POST',
                headers: {{
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCSRFToken()
                }}
            }})
            .then(response => response.json())
            .then(data => {{
                if (data.success) {{
                    showSuccess(data.message);
                    // Recharger la liste des employés
                    loadSPAContent('employees');
                }} else {{
                    showError('Erreur: ' + (data.error || 'Suppression échouée'));
                }}
            }})
            .catch(error => {{
                showError('Erreur de connexion: ' + error.message);
            }});
        }}

        // Export Excel
        function exportToExcel() {{
            console.log('📥 Export Excel');
            
            fetch('/api/export_employees/', {{
                headers: {{
                    'X-Requested-With': 'XMLHttpRequest',
                }}
            }})
            .then(response => {{
                if (response.ok) {{
                    return response.blob().then(blob => {{
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `employes_${{new Date().toISOString().split('T')[0]}}.xlsx`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        window.URL.revokeObjectURL(url);
                        showSuccess('Export terminé avec succès');
                    }});
                }} else {{
                    throw new Error('Erreur HTTP: ' + response.status);
                }}
            }})
            .catch(error => {{
                showError('Erreur lors de l\\'export: ' + error.message);
            }});
        }}

        // ===== FONCTIONS DE FILTRAGE =====

        function filterEmployees() {{
            console.log('🔍 Filtrage des employés');
            
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const selectedSite = document.getElementById('siteFilter').value;
            const selectedDept = document.getElementById('deptFilter').value;
            
            const rows = document.querySelectorAll('.employee-row');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                const siteId = row.getAttribute('data-site');
                const deptId = row.getAttribute('data-dept');
                
                const matchesSearch = !searchTerm || text.includes(searchTerm);
                const matchesSite = !selectedSite || siteId === selectedSite;
                const matchesDept = !selectedDept || deptId === selectedDept;
                
                if (matchesSearch && matchesSite && matchesDept) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            // Mettre à jour les compteurs
            document.getElementById('employeeCount').textContent = visibleCount;
            document.getElementById('filterResults').textContent = 
                visibleCount === rows.length ? 
                `${{visibleCount}} employé(s)` : 
                `${{visibleCount}} sur ${{rows.length}} employé(s)`;
            
            // Afficher/masquer le message "aucun résultat"
            const noResults = document.getElementById('noResults');
            const tableBody = document.getElementById('employeesTableBody');
            if (visibleCount === 0) {{
                noResults.style.display = 'block';
                tableBody.style.display = 'none';
            }} else {{
                noResults.style.display = 'none';
                tableBody.style.display = '';
            }}
        }}

        function clearAllFilters() {{
            console.log('🧹 Effacement des filtres');
            document.getElementById('searchInput').value = '';
            document.getElementById('siteFilter').value = '';
            document.getElementById('deptFilter').value = '';
            filterEmployees();
        }}

        // ===== FONCTIONS UTILITAIRES =====

        function displayEmployeeDetails(data) {{
            const emp = data.employe;
            const bulletins = data.bulletins || [];
            const absences = data.absences || [];
            
            let bulletinsHtml = bulletins.length ? 
                bulletins.map(b => `
                    <tr>
                        <td>${{b.mois}}/${{b.annee}}</td>
                        <td class="text-end">${{b.salaire_brut.toLocaleString()}} DH</td>
                        <td class="text-end">${{b.salaire_net.toLocaleString()}} DH</td>
                        <td><span class="badge bg-${{b.statut === 'valide' ? 'success' : 'warning'}}">${{b.statut}}</span></td>
                    </tr>
                `).join('') : '<tr><td colspan="4" class="text-center text-muted">Aucun bulletin de paie</td></tr>';
            
            let absencesHtml = absences.length ?
                absences.map(a => `
                    <tr>
                        <td>${{a.type_absence}}</td>
                        <td>${{a.date_debut}} → ${{a.date_fin}}</td>
                        <td class="text-center">${{a.nombre_jours}} jour(s)</td>
                        <td><span class="badge bg-${{a.statut === 'approuve' ? 'success' : 'warning'}}">${{a.statut}}</span></td>
                    </tr>
                `).join('') : '<tr><td colspan="4" class="text-center text-muted">Aucune absence enregistrée</td></tr>';
            
            const detailsHtml = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0"><i class="fas fa-user me-2"></i>Informations Personnelles</h6>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm table-borderless">
                                    <tr><th width="120">Matricule:</th><td><strong>${{emp.matricule}}</strong></td></tr>
                                    <tr><th>Nom complet:</th><td><strong>${{emp.nom}} ${{emp.prenom}}</strong></td></tr>
                                    <tr><th>Fonction:</th><td>${{emp.fonction || 'Non défini'}}</td></tr>
                                    <tr><th>Salaire de base:</th><td class="text-success fw-bold">${{emp.salaire_base.toLocaleString()}} DH</td></tr>
                                    <tr><th>Date d'embauche:</th><td>${{emp.date_embauche || 'Non défini'}}</td></tr>
                                    <tr><th>Téléphone:</th><td>${{emp.telephone || 'Non défini'}}</td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header bg-info text-white">
                                <h6 class="mb-0"><i class="fas fa-cog me-2"></i>Informations Système</h6>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm table-borderless">
                                    <tr><th width="120">Site:</th><td>${{emp.site || 'Non assigné'}}</td></tr>
                                    <tr><th>Département:</th><td>${{emp.departement || 'Non assigné'}}</td></tr>
                                    <tr><th>Statut:</th><td><span class="badge bg-${{emp.actif ? 'success' : 'secondary'}}">${{emp.actif ? 'Actif' : 'Inactif'}}</span></td></tr>
                                    ${{emp.user ? `
                                    <tr><th>Email:</th><td>${{emp.user.email}}</td></tr>
                                    <tr><th>Utilisateur:</th><td>${{emp.user.username}}</td></tr>
                                    <tr><th>Dernière connexion:</th><td>${{emp.user.last_login}}</td></tr>
                                    ` : '<tr><th colspan="2" class="text-muted">Aucun compte utilisateur associé</th></tr>'}}
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-success text-white">
                                <h6 class="mb-0"><i class="fas fa-file-invoice-dollar me-2"></i>Derniers Bulletins de Paie</h6>
                            </div>
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-sm mb-0">
                                        <thead class="table-light">
                                            <tr><th>Période</th><th>Salaire Brut</th><th>Salaire Net</th><th>Statut</th></tr>
                                        </thead>
                                        <tbody>${{bulletinsHtml}}</tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header bg-warning text-white">
                                <h6 class="mb-0"><i class="fas fa-calendar-times me-2"></i>Dernières Absences</h6>
                            </div>
                            <div class="card-body p-0">
                                <div class="table-responsive">
                                    <table class="table table-sm mb-0">
                                        <thead class="table-light">
                                            <tr><th>Type</th><th>Période</th><th>Durée</th><th>Statut</th></tr>
                                        </thead>
                                        <tbody>${{absencesHtml}}</tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('employeeDetailsModalBody').innerHTML = detailsHtml;
        }}

        function showModal(modalId) {{
            // Essayer différentes méthodes pour ouvrir le modal
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {{
                const modal = new bootstrap.Modal(document.getElementById(modalId));
                modal.show();
            }} else if (typeof $ !== 'undefined' && $.fn.modal) {{
                $(`#${{modalId}}`).modal('show');
            }} else {{
                // Fallback basique
                const modal = document.getElementById(modalId);
                modal.style.display = 'block';
                modal.classList.add('show');
                modal.setAttribute('aria-hidden', 'false');
            }}
        }}

        function getCSRFToken() {{
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {{
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {{
                    return value;
                }}
            }}
            return '';
        }}

        function showSuccess(message) {{
            if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                PayrollPro.notify(message, 'success');
            }} else {{
                alert('✅ ' + message);
            }}
        }}

        function showError(message) {{
            if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                PayrollPro.notify(message, 'error');
            }} else {{
                alert('❌ ' + message);
            }}
        }}

        // Initialiser les filtres au chargement
        document.addEventListener('DOMContentLoaded', function() {{
            filterEmployees();
        }});

        console.log('✅ Script SPA Employés initialisé avec succès');
        </script>
        '''

        data = {
            'success': True,
            'content': html_content
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement des employés: {str(e)}'
        })

@login_required
def spa_absences(request):
    """Contenu de la gestion des absences pour SPA"""
    try:
        # Récupérer les absences
        absences = Absence.objects.all().select_related('employe')[:20]  # Limite à 20 pour la démo
        
        # Statistiques des absences
        stats = {
            'en_attente': Absence.objects.filter(statut='EN_ATTENTE').count(),
            'approuvees': Absence.objects.filter(statut='APPROUVE').count(),
            'refusees': Absence.objects.filter(statut='REFUSE').count(),
            'total': Absence.objects.count()
        }
        
        # Construire le HTML des absences
        absences_html = ""
        for absence in absences:
            status_class = {
                'EN_ATTENTE': 'badge-warning',
                'APPROUVE': 'badge-success',
                'REFUSE': 'badge-danger'
            }.get(absence.statut, 'badge-secondary')
            
            absences_html += f'''
            <tr class="clickable">
                <td><strong>{absence.employe.nom} {absence.employe.prenom}</strong></td>
                <td>{absence.type_absence}</td>
                <td>{absence.date_debut.strftime('%d/%m/%Y')}</td>
                <td>{absence.date_fin.strftime('%d/%m/%Y')}</td>
                <td>{absence.nombre_jours} jour(s)</td>
                <td><span class="badge {status_class}">{absence.statut}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-success me-1" onclick="PayrollPro.notify('Approbation absence #{absence.id}', 'success')">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger me-1" onclick="PayrollPro.notify('Refus absence #{absence.id}', 'warning')">
                        <i class="fas fa-times"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-info" onclick="PayrollPro.notify('Détails absence #{absence.id}', 'info')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
            '''
        
        data = {
            'success': True,
            'content': f'''
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient mb-4">
                        <i class="fas fa-calendar-alt me-3"></i>Gestion des Absences
                    </h2>
                </div>
            </div>
            
            <!-- Statistiques des absences -->
            <div class="row mb-4">
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift" style="border-left-color: #f59e0b;">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{stats['en_attente']}</div>
                                <div class="stats-label">En Attente</div>
                            </div>
                            <div class="icon-wrapper" style="background: var(--warning-gradient);">
                                <i class="fas fa-clock"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift" style="border-left-color: #10b981;">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{stats['approuvees']}</div>
                                <div class="stats-label">Approuvées</div>
                            </div>
                            <div class="icon-wrapper" style="background: var(--success-gradient);">
                                <i class="fas fa-check"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift" style="border-left-color: #ef4444;">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{stats['refusees']}</div>
                                <div class="stats-label">Refusées</div>
                            </div>
                            <div class="icon-wrapper" style="background: var(--danger-gradient);">
                                <i class="fas fa-times"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift">
                        <div class="d-flex align-items-center justify-content-between">
                            <div>
                                <div class="stats-number">{stats['total']}</div>
                                <div class="stats-label">Total</div>
                            </div>
                            <div class="icon-wrapper">
                                <i class="fas fa-calendar"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Liste des absences -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card slide-in-up">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h4><i class="fas fa-calendar-alt me-2"></i>Demandes d'Absences</h4>
                                <div>
                                    <button class="btn btn-success me-2" onclick="PayrollPro.notify('Fonctionnalité: Nouvelle absence', 'info')">
                                        <i class="fas fa-plus me-2"></i>Nouvelle Absence
                                    </button>
                                    <button class="btn btn-primary" onclick="PayrollPro.notify('Fonctionnalité: Export calendrier', 'info')">
                                        <i class="fas fa-calendar-export me-2"></i>Export Calendrier
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Employé</th>
                                            <th>Type</th>
                                            <th>Date Début</th>
                                            <th>Date Fin</th>
                                            <th>Durée</th>
                                            <th>Statut</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {absences_html}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Scripts JavaScript pour les actions d'absences -->
            <script>
            // Fonctions de gestion des absences corrigées
            function approveAbsence(absenceId) {{
                if (confirm('Approuver cette demande d\\'absence ?')) {{
                    PayrollPro.notify('Traitement en cours...', 'info');
                    
                    PayrollPro.utils.apiCall(`/api/absence/${{absenceId}}/approve/`, {{
                        method: 'POST',
                        body: JSON.stringify({{action: 'approve'}})
                    }})
                    .then(data => {{
                        if (data.success) {{
                            PayrollPro.notify('Absence approuvée avec succès', 'success');
                            loadSPAContent('absences'); // Recharger la liste
                        }} else {{
                            PayrollPro.notify('Erreur: ' + data.error, 'error');
                        }}
                    }})
                    .catch(error => {{
                        PayrollPro.notify('Erreur de connexion', 'error');
                    }});
                }}
            }}
            
            function rejectAbsence(absenceId) {{
                const motif = prompt('Motif du refus (optionnel):');
                if (motif !== null) {{
                    PayrollPro.notify('Traitement en cours...', 'info');
                    
                    PayrollPro.utils.apiCall(`/api/absence/${{absenceId}}/reject/`, {{
                        method: 'POST',
                        body: JSON.stringify({{action: 'reject', motif: motif}})
                    }})
                    .then(data => {{
                        if (data.success) {{
                            PayrollPro.notify('Absence refusée', 'warning');
                            loadSPAContent('absences');
                        }} else {{
                            PayrollPro.notify('Erreur: ' + data.error, 'error');
                        }}
                    }});
                }}
            }}
            
            function viewAbsence(absenceId) {{
                PayrollPro.notify(`Ouverture détails absence #${{absenceId}}`, 'info');
                window.open(`/absence/${{absenceId}}/details/`, '_blank');
            }}
            
            function filterAbsences(statut) {{
                PayrollPro.notify(`Filtrage par statut: ${{statut}}`, 'info');
                loadSPAContent('absences', {{filter: statut}});
            }}
            
            // Fonction de sécurité pour PayrollPro.notify
            if (typeof PayrollPro === 'undefined') {{
                window.PayrollPro = {{
                    notify: function(message, type) {{
                        console.log(`${{type}}: ${{message}}`);
                        alert(message);
                    }}
                }};
            }}
            </script>
            '''
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement des absences: {str(e)}'
        })

@login_required
def spa_payroll(request):
    """Contenu du calcul de paie pour SPA"""
    try:
        # Statistiques pour le calcul de paie
        employes_count = Employe.objects.filter(actif=True).count()
        bulletins_mois = BulletinPaie.objects.filter(
            date_creation__month=datetime.now().month,
            date_creation__year=datetime.now().year
        ).count()
        
        # Récupérer quelques employés pour la démo
        employes = Employe.objects.filter(actif=True)[:10]
        
        employes_html = ""
        for employe in employes:
            employes_html += f'''
            <div class="col-lg-6 col-xl-4 mb-3">
                <div class="card h-100 hover-lift">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <div class="icon-wrapper small me-3">
                                <i class="fas fa-user"></i>
                            </div>
                            <div>
                                <h6 class="mb-0">{employe.nom} {employe.prenom}</h6>
                                <small class="text-muted">{employe.fonction or 'Fonction non définie'}</small>
                            </div>
                        </div>
                        <div class="row text-center">
                            <div class="col-6">
                                <div class="stats-number" style="font-size: 1.2rem;">{employe.salaire_base:,.0f}</div>
                                <div class="stats-label" style="font-size: 0.8rem;">Salaire Base</div>
                            </div>
                            <div class="col-6">
                                <span class="badge badge-success">Actif</span>
                            </div>
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-sm btn-primary w-100" onclick="PayrollPro.notify('Calcul paie pour {employe.nom}', 'info')">
                                <i class="fas fa-calculator me-1"></i>Calculer
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            '''
        
        data = {
            'success': True,
            'content': f'''
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient mb-4">
                        <i class="fas fa-money-bill-wave me-3"></i>Calcul de Paie
                    </h2>
                </div>
            </div>
            
            <!-- Actions principales -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card slide-in-up">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h4><i class="fas fa-calculator me-2"></i>Centre de Calcul</h4>
                                <div>
                                    <button class="btn btn-success me-2" onclick="PayrollPro.notify('Calcul en lot démarré', 'success')">
                                        <i class="fas fa-play me-2"></i>Calculer Tout
                                    </button>
                                    <button class="btn btn-primary" onclick="PayrollPro.notify('Aperçu du calcul généré', 'info')">
                                        <i class="fas fa-eye me-2"></i>Aperçu Calcul
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-lg-4">
                                    <div class="stats-card text-center">
                                        <div class="stats-number">{employes_count}</div>
                                        <div class="stats-label">Employés à Traiter</div>
                                    </div>
                                </div>
                                <div class="col-lg-4">
                                    <div class="stats-card text-center">
                                        <div class="stats-number">{bulletins_mois}</div>
                                        <div class="stats-label">Bulletins ce Mois</div>
                                    </div>
                                </div>
                                <div class="col-lg-4">
                                    <div class="stats-card text-center">
                                        <div class="stats-number">{datetime.now().strftime('%m/%Y')}</div>
                                        <div class="stats-label">Période Active</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Liste des employés -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card slide-in-up">
                        <div class="card-header">
                            <h5><i class="fas fa-users me-2"></i>Employés Disponibles pour Calcul</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                {employes_html}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement du calcul de paie: {str(e)}'
        })

@login_required
def spa_reports(request):
    """Contenu des rapports et exports pour SPA"""
    data = {
        'success': True,
        'content': '''
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="text-gradient mb-4">
                    <i class="fas fa-chart-bar me-3"></i>Rapports & Exports
                </h2>
            </div>
        </div>
        
        <!-- Options d'export -->
        <div class="row mb-4">
            <div class="col-lg-6 mb-3">
                <div class="card slide-in-up hover-lift">
                    <div class="card-header">
                        <h5><i class="fas fa-file-excel me-2"></i>Exports Excel</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button class="btn btn-success" onclick="PayrollPro.notify('Export liste employés démarré', 'success')">
                                <i class="fas fa-users me-2"></i>Liste des Employés
                            </button>
                            <button class="btn btn-success" onclick="PayrollPro.notify('Export bulletins démarré', 'success')">
                                <i class="fas fa-file-invoice me-2"></i>Bulletins de Paie
                            </button>
                            <button class="btn btn-success" onclick="PayrollPro.notify('Export CNSS démarré', 'success')">
                                <i class="fas fa-building me-2"></i>Déclaration CNSS
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-6 mb-3">
                <div class="card slide-in-up hover-lift" style="animation-delay: 0.1s;">
                    <div class="card-header">
                        <h5><i class="fas fa-file-pdf me-2"></i>Rapports PDF</h5>
                    </div>
                    <div class="card-body">
                        <div class="d-grid gap-2">
                            <button class="btn btn-danger" onclick="PayrollPro.notify('Rapport masse salariale généré', 'success')">
                                <i class="fas fa-money-bill-wave me-2"></i>Masse Salariale
                            </button>
                            <button class="btn btn-danger" onclick="PayrollPro.notify('Rapport absences généré', 'success')">
                                <i class="fas fa-calendar-times me-2"></i>Rapport Absences
                            </button>
                            <button class="btn btn-danger" onclick="PayrollPro.notify('Statistiques RH générées', 'success')">
                                <i class="fas fa-chart-line me-2"></i>Statistiques RH
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Graphiques et statistiques -->
        <div class="row">
            <div class="col-12">
                <div class="card slide-in-up" style="animation-delay: 0.2s;">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-pie me-2"></i>Aperçu des Données</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Module en développement :</strong> Les graphiques et tableaux de bord avancés seront disponibles dans la prochaine version.
                        </div>
                        <div class="text-center">
                            <button class="btn btn-modern" onclick="PayrollPro.notify('Fonctionnalité bientôt disponible !', 'info')">
                                <i class="fas fa-chart-area me-2"></i>Voir Graphiques Avancés
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
    }
    
    return JsonResponse(data)
