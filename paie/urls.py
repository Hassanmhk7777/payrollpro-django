
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from . import views
from . import views_excel  # Import des vues Excel
from . import views_spa  # Import des vues SPA
from . import views_spa_fixed  # Import des vues SPA corrigées
from . import views_rubriques_complete  # Import des nouvelles vues rubriques

app_name = 'paie'

# ==============================================================================
# PATTERNS D'URL - PAYROLLPRO
# ==============================================================================

from . import views

def test_fonctionnalites(request):
    """Page de test pour vérifier toutes les fonctionnalités"""
    from django.shortcuts import render
    return render(request, 'paie/test_fonctionnalites.html')

urlpatterns = [
    # Page de test des fonctionnalités
    path('test/', test_fonctionnalites, name='test_fonctionnalites'),
    
    # Redirection par défaut vers la version moderne
    path('', lambda request: redirect('paie:accueil_moderne', permanent=False)),
    path('accueil/', views.accueil, name='accueil'),
    # Page moderne principale SPA
    path('accueil_moderne/', views.accueil_moderne, name='accueil_moderne'),
    
    # API SPA pour chargement dynamique de contenu - Versions corrigées
    path('api/spa/dashboard/', views_spa_fixed.spa_dashboard_fixed, name='spa_dashboard'),
    path('api/spa/dashboard-admin/', views_spa_fixed.spa_dashboard_admin_fixed, name='spa_dashboard_admin'),
    path('api/spa/dashboard-rh/', views_spa_fixed.spa_dashboard_rh_fixed, name='spa_dashboard_rh'),
    path('api/spa/employees/', views_spa.spa_employees, name='spa_employees'),
    path('api/spa/absences/', views_spa.spa_absences, name='spa_absences'),
    path('api/spa/payroll/', views_spa_fixed.spa_payroll_fixed, name='spa_payroll'),
    path('api/spa/reports/', views_spa.spa_reports, name='spa_reports'),
    path('api/spa/rubriques/', views_rubriques_complete.rubriques_spa_view, name='spa_rubriques'),
    
    # Rubriques personnalisées - AJAX endpoints
    path('rubriques/creer/', views_rubriques_complete.creer_rubrique_ajax, name='creer_rubrique_ajax'),
    path('rubriques/<int:rubrique_id>/', views_rubriques_complete.rubrique_details_ajax, name='rubrique_details_ajax'),
    path('rubriques/<int:rubrique_id>/activer/', views_rubriques_complete.activer_rubrique_ajax, name='activer_rubrique_ajax'),
    path('rubriques/<int:rubrique_id>/supprimer/', views_rubriques_complete.supprimer_rubrique_ajax, name='supprimer_rubrique_ajax'),
    path('rubriques/<int:rubrique_id>/assigner/', views_rubriques_complete.assigner_employes_ajax, name='assigner_employes_ajax'),
    path('rubriques/tester-formule/', views_rubriques_complete.tester_formule_ajax, name='tester_formule_ajax'),
    # Dashboards réels
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/rh/', views.dashboard_rh, name='dashboard_rh'),
    path('dashboard/employe/', views.dashboard_employe, name='dashboard_employe'),
    # Dashboards modernes
    path('dashboard/admin/moderne/', views.dashboard_admin_moderne, name='dashboard_admin_moderne'),
    path('dashboard/rh/moderne/', views.dashboard_rh_moderne, name='dashboard_rh_moderne'),
    # Pages principales
    path('gestion-absences/', views.gestion_absences, name='gestion_absences_moderne'),
    path('liste-employes/', views.liste_employes, name='liste_employes'),
    path('gestion-utilisateurs/', views.creer_compte_employe, name='gestion_utilisateurs'),
    path('calcul-paie/', views.calcul_paie, name='calcul_paie'),
    path('aide/', views.aide, name='aide'),
    path('deconnexion/', views.deconnexion_vue, name='deconnexion'),
    # Excel et exports
    path('export/cnss/excel/', views_excel.export_cnss_excel, name='export_cnss_excel'),
    path('export/statistiques/excel/', views_excel.statistiques_excel, name='statistiques_excel'),
    path('export/cnss/<int:mois>/<int:annee>/', views_excel.export_cnss_mensuel, name='export_cnss_mensuel'),
    # API Routes pour les absences
    path('api/absence/<int:absence_id>/approve/', views.api_approve_absence, name='api_approve_absence'),
    path('api/absence/<int:absence_id>/reject/', views.api_reject_absence, name='api_reject_absence'),
    # API Routes pour le calcul de paie
    path('api/payroll/calculate/<int:employe_id>/', views.api_calculate_payroll, name='api_calculate_payroll'),
    path('api/payroll/calculate-all/', views.api_calculate_all_payroll, name='api_calculate_all_payroll'),
    path('api/payroll/export/', views.api_export_payroll, name='api_export_payroll'),
    # Compatibilité pour anciens liens
    path('employes/', lambda request: redirect('paie:liste_employes', permanent=True)),
    path('absences/', lambda request: redirect('paie:gestion_absences_moderne', permanent=True)),
    # Version corrigée de l'accueil moderne
    path('accueil_moderne_fixed/', views.accueil_moderne_fixed, name='accueil_moderne_fixed'),
]