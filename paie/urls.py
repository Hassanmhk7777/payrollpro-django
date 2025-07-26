
from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from . import views
from . import views_excel  # Import des vues Excel
from . import views_spa  # Import des vues SPA

app_name = 'paie'

# Vues temporaires simples pour éviter les erreurs
def dashboard_admin_moderne(request):
    return HttpResponse("""
    <h1>🏢 Dashboard Admin Moderne</h1>
    <p>Dashboard administrateur en cours de configuration...</p>
    <a href="/admin/">← Retour à l'administration</a>
    """)

def dashboard_rh_moderne(request):
    return HttpResponse("""
    <h1>👥 Dashboard RH Moderne</h1>
    <p>Dashboard RH en cours de configuration...</p>
    <a href="/admin/">← Retour à l'administration</a>
    """)

def dashboard_employe_moderne(request):
    return HttpResponse("""
    <h1>💼 Dashboard Employé</h1>
    <p>Dashboard employé en cours de configuration...</p>
    <a href="/admin/">← Retour à l'administration</a>
    """)

def gestion_absences_moderne(request):
    return HttpResponse("""
    <h1>📅 Gestion des Absences</h1>
    <p>Module de gestion des absences en cours de configuration...</p>
    <a href="/admin/">← Retour à l'administration</a>
    """)

def liste_employes_moderne(request):
    return HttpResponse("""
    <h1>👥 Liste des Employés</h1>
    <p>Module de gestion des employés en cours de configuration...</p>
    <a href="/admin/">← Retour à l'administration</a>
    """)

def calcul_paie_moderne(request):
    return HttpResponse("""
    <h1>💰 Calcul de Paie</h1>
    <p>Module de calcul de paie en cours de configuration...</p>
    <a href="/admin/">← Retour à l'administration</a>
    """)

def gestion_utilisateurs_moderne(request):
    return HttpResponse("""
    <h1>👤 Gestion des Utilisateurs</h1>
    <p>Module de gestion des utilisateurs en cours de configuration...</p>
    <a href="/admin/">← Retour à l'administration</a>
    """)

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
    
    # API SPA pour chargement dynamique de contenu
    path('api/spa/dashboard/', views_spa.spa_dashboard, name='spa_dashboard'),
    path('api/spa/dashboard-admin/', views_spa.spa_dashboard_admin, name='spa_dashboard_admin'),
    path('api/spa/dashboard-rh/', views_spa.spa_dashboard_rh, name='spa_dashboard_rh'),
    path('api/spa/employees/', views_spa.spa_employees, name='spa_employees'),
    path('api/spa/absences/', views_spa.spa_absences, name='spa_absences'),
    path('api/spa/payroll/', views_spa.spa_payroll, name='spa_payroll'),
    path('api/spa/reports/', views_spa.spa_reports, name='spa_reports'),
    # Dashboards réels
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/rh/', views.dashboard_rh, name='dashboard_rh'),
    path('dashboard/employe/', views.dashboard_employe, name='dashboard_employe'),
    # Dashboards modernes
    path('dashboard/admin/moderne/', views.dashboard_admin_moderne, name='dashboard_admin_moderne'),
    path('dashboard/rh/moderne/', views.dashboard_rh_moderne, name='dashboard_rh_moderne'),
    path('dashboard/employe/moderne/', dashboard_employe_moderne, name='dashboard_employe_moderne'),
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
    # URLs temporaires (gardez-les si besoin)
    path('absences/moderne/', gestion_absences_moderne, name='gestion_absences_moderne_temp'),
    path('employes/moderne/', liste_employes_moderne, name='liste_employes_moderne'),
    path('calcul-paie/moderne/', calcul_paie_moderne, name='calcul_paie_moderne'),
    path('utilisateurs/moderne/', gestion_utilisateurs_moderne, name='gestion_utilisateurs_moderne'),
    # Compatibilité pour anciens liens
    path('employes/', lambda request: redirect('paie:liste_employes', permanent=True)),
    path('absences/', lambda request: redirect('paie:gestion_absences_moderne', permanent=True)),
]