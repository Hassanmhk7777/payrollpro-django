from django.urls import path
from . import views
from . import views_users
from . import views_excel

app_name = 'paie'

urlpatterns = [
    # Pages principales
    path('', views.accueil, name='accueil'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/rh/', views.dashboard_rh, name='dashboard_rh'),
    path('dashboard/employe/', views.dashboard_employe, name='dashboard_employe'),
    
    # Gestion des employés
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/<int:employe_id>/', views.detail_employe, name='detail_employe'),
    
    # Calcul de paie
    path('calcul-paie/', views.calcul_paie, name='calcul_paie'),
    path('bulletin/<int:bulletin_id>/pdf/', views.generer_bulletin_pdf, name='bulletin_pdf'),
    
    # Gestion des absences
    path('absences/', views.gestion_absences, name='gestion_absences'),
    path('absences/<int:absence_id>/valider/', views.valider_absence, name='valider_absence'),
    path('absences/validation-lot/', views.validation_lot_absences, name='validation_lot_absences'),
    path('absences/statistiques/', views.statistiques_absences, name='statistiques_absences'),
    path('calendrier-absences/', views.calendrier_absences, name='calendrier_absences'),
    path('test-absences/', views.test_calcul_absences, name='test_calcul_absences'),
    
    # ===== GESTION DES UTILISATEURS - URLs de base =====
    path('gestion-utilisateurs/', views_users.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('gestion-utilisateurs/creer/<int:employe_id>/', views_users.creer_compte_employe, name='creer_compte_employe'),
    path('gestion-utilisateurs/modifier-role/<int:employe_id>/', views_users.modifier_role_employe, name='modifier_role_employe'),
    path('gestion-utilisateurs/desactiver/<int:employe_id>/', views_users.desactiver_compte, name='desactiver_compte'),
    path('gestion-utilisateurs/reactiver/<int:employe_id>/', views_users.reactiver_compte, name='reactiver_compte'),
    path('gestion-utilisateurs/reinitialiser-mdp/<int:employe_id>/', views_users.reinitialiser_mot_de_passe, name='reinitialiser_mot_de_passe'),
    
    # APIs principales
    path('api/infos-session/', views_users.obtenir_infos_session, name='infos_session'),
    path('api/statistiques-utilisateurs/', views_users.statistiques_utilisateurs, name='statistiques_utilisateurs'),
    # Page d'aide
    path('aide/', views.page_aide, name='aide'),
    
    # Déconnexion
    path('deconnexion/', views.deconnexion_vue, name='deconnexion'),
    path('connexion/', views.connexion_personnalisee, name='connexion_personnalisee'),
    path('creer-comptes/', views.creer_compte_employe, name='creer_comptes'),

     # ===== EXPORTS EXCEL - NOUVEAUX =====
    path('export-excel/bulletins/', views_excel.export_bulletins_massif_excel, name='export_bulletins_excel'),
    path('export-excel/bulletin/<int:bulletin_id>/', views_excel.export_bulletin_excel, name='export_bulletin_excel'),
    path('export-excel/cnss/', views_excel.export_cnss_excel, name='export_cnss_excel'),
    path('export-excel/statistiques/', views_excel.statistiques_excel, name='statistiques_excel'),
    path('export-excel/cnss/', views_excel.page_export_cnss, name='page_export_cnss'),
    path('export-excel/cnss/<int:mois>/<int:annee>/', views_excel.export_cnss_mensuel, name='export_cnss_mensuel'),
]