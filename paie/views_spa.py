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
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def spa_employees(request):
    """Contenu de la gestion des employés pour SPA"""
    try:
        # Récupérer les employés
        employes = Employe.objects.filter(actif=True).select_related('site', 'departement')
        
        # Construire le HTML des employés
        employes_html = ""
        for employe in employes:
            employes_html += f'''
            <tr class="clickable">
                <td><strong>{employe.nom} {employe.prenom}</strong></td>
                <td>{employe.fonction or 'Non défini'}</td>
                <td><span class="highlight">{employe.salaire_base:,.0f} DH</span></td>
                <td>{employe.site.nom if employe.site else 'Non assigné'}</td>
                <td>{employe.departement.nom if employe.departement else 'Non assigné'}</td>
                <td><span class="badge badge-success">Actif</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="PayrollPro.notify('Consultation employé #{employe.id}', 'info')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning me-1" onclick="PayrollPro.notify('Édition employé #{employe.id}', 'info')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="PayrollPro.notify('Suppression employé #{employe.id}', 'warning')">
                        <i class="fas fa-trash"></i>
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
                        <i class="fas fa-users me-3"></i>Gestion des Employés
                    </h2>
                </div>
            </div>
            
            <!-- Actions principales -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card slide-in-up">
                        <div class="card-header">
                            <div class="d-flex justify-content-between align-items-center">
                                <h4><i class="fas fa-users me-2"></i>Liste des Employés ({employes.count()})</h4>
                                <div>
                                    <button class="btn btn-success me-2" onclick="PayrollPro.notify('Fonctionnalité: Ajouter un employé', 'info')">
                                        <i class="fas fa-user-plus me-2"></i>Ajouter Employé
                                    </button>
                                    <button class="btn btn-primary" onclick="PayrollPro.notify('Fonctionnalité: Import Excel', 'info')">
                                        <i class="fas fa-file-import me-2"></i>Import Excel
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Nom Complet</th>
                                            <th>Fonction</th>
                                            <th>Salaire</th>
                                            <th>Site</th>
                                            <th>Département</th>
                                            <th>Status</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {employes_html}
                                    </tbody>
                                </table>
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
            date_calcul__month=datetime.now().month,
            date_calcul__year=datetime.now().year
        ).count()
        
        # Récupérer quelques employés pour la démo
        employes = Employe.objects.filter(actif=True)[:10]
        
        # Ajouter des informations aux employés
        employes_avec_info = []
        for employe in employes:
            bulletin_existant = BulletinPaie.objects.filter(
                employe=employe,
                mois=datetime.now().month,
                annee=datetime.now().year
            ).exists()
            employe.bulletin_existant = bulletin_existant
            employes_avec_info.append(employe)
        
        # Contexte pour le template
        context = {
            'employes_count': employes_count,
            'bulletins_mois': bulletins_mois,
            'mois_annee': datetime.now().strftime('%m/%Y'),
            'en_attente': employes_count - bulletins_mois,
            'employes': employes_avec_info,
        }
        
        # Render du template
        html_content = render(request, 'paie/spa/payroll.html', context).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'content': html_content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement du module calcul de paie: {str(e)}'
        })

@login_required
def spa_reports(request):
    """Contenu des rapports pour SPA"""
    try:
        # Statistiques pour les rapports
        total_employes = Employe.objects.filter(actif=True).count()
        total_bulletins = BulletinPaie.objects.count()
        masse_salariale = sum(emp.salaire_base for emp in Employe.objects.filter(actif=True))
        
        data = {
            'success': True,
            'content': f'''
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient mb-4">
                        <i class="fas fa-chart-bar me-3"></i>Rapports et Analyses
                    </h2>
                </div>
            </div>
            
            <!-- Statistiques rapides -->
            <div class="row mb-4">
                <div class="col-lg-4 col-md-6 mb-3">
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
                
                <div class="col-lg-4 col-md-6 mb-3">
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
                
                <div class="col-lg-4 col-md-6 mb-3">
                    <div class="stats-card slide-in-up hover-lift" style="animation-delay: 0.2s;">
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
            
            <!-- Actions de rapport -->
            <div class="row">
                <div class="col-lg-6 mb-4">
                    <div class="card slide-in-up">
                        <div class="card-header">
                            <h5><i class="fas fa-file-export me-2"></i>Rapports Automatisés</h5>
                        </div>
                        <div class="card-body">
                            <div class="d-grid gap-2">
                                <button class="btn btn-danger" onclick="PayrollPro.notify('Rapport masse salariale généré', 'success')">
                                    <i class="fas fa-money-bill-wave me-2"></i>Masse Salariale
                                </button>
                                <button class="btn btn-warning" onclick="PayrollPro.notify('Rapport absences généré', 'success')">
                                    <i class="fas fa-calendar-times me-2"></i>Rapport Absences
                                </button>
                                <button class="btn btn-info" onclick="PayrollPro.notify('Statistiques RH générées', 'success')">
                                    <i class="fas fa-chart-line me-2"></i>Statistiques RH
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-6 mb-4">
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
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement des rapports: {str(e)}'
        })
