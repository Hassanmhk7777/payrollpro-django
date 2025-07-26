from django.urls import path
from . import views
from . import views_users
from . import views_excel
from . import views_advanced

app_name = 'paie'

urlpatterns = [
    # Pages principales
    path('', views.accueil, name='accueil'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/rh/', views.dashboard_rh, name='dashboard_rh'),
    path('dashboard/employe/', views.dashboard_employe, name='dashboard_employe'),
    
    # ===== NOUVELLES INTERFACES MODERNES (remplacent les anciennes) =====
    
    # Gestion des employés - VERSION MODERNE
    path('employes/', views_advanced.liste_employes_avancee, name='liste_employes'),
    path('employes/<int:employe_id>/', views.detail_employe, name='detail_employe'),
    path('employes/moderne/', views_advanced.liste_employes_avancee, name='liste_employes_moderne'),
    path('employes/export-filtre/', views_advanced.export_employes_excel_avance, name='export_employes_filtre'),
    
    # Calcul de paie - VERSION MODERNE
    path('calcul-paie/', views_advanced.calcul_paie_avance, name='calcul_paie'),
    path('calcul-paie/moderne/', views_advanced.calcul_paie_avance, name='calcul_paie_moderne'),
    path('bulletin/<int:bulletin_id>/pdf/', views.generer_bulletin_pdf, name='bulletin_pdf'),
    
    # Gestion des absences - VERSION MODERNE
    path('absences/', views_advanced.gestion_absences_avancee, name='gestion_absences'),
    path('absences/moderne/', views_advanced.gestion_absences_avancee, name='gestion_absences_moderne'),
    path('absences/<int:absence_id>/valider/', views.valider_absence, name='valider_absence'),
    path('absences/validation-lot/', views.validation_lot_absences, name='validation_lot_absences'),
    path('absences/statistiques/', views.statistiques_absences, name='statistiques_absences'),
    path('calendrier-absences/', views.calendrier_absences, name='calendrier_absences'),
    path('test-absences/', views.test_calcul_absences, name='test_calcul_absences'),
    
    # Gestion des utilisateurs - VERSION MODERNE
    path('gestion-utilisateurs/', views_advanced.gestion_utilisateurs_avancee, name='gestion_utilisateurs'),
    path('utilisateurs/moderne/', views_advanced.gestion_utilisateurs_avancee, name='gestion_utilisateurs_moderne'),
    path('gestion-utilisateurs/creer/<int:employe_id>/', views_users.creer_compte_employe, name='creer_compte_employe'),
    path('gestion-utilisateurs/modifier-role/<int:employe_id>/', views_users.modifier_role_employe, name='modifier_role_employe'),
    path('gestion-utilisateurs/desactiver/<int:employe_id>/', views_users.desactiver_compte, name='desactiver_compte'),
    path('gestion-utilisateurs/reactiver/<int:employe_id>/', views_users.reactiver_compte, name='reactiver_compte'),
    path('gestion-utilisateurs/reinitialiser-mdp/<int:employe_id>/', views_users.reinitialiser_mot_de_passe, name='reinitialiser_mot_de_passe'),
    
    # ===== APIs POUR FILTRES DYNAMIQUES =====
    path('api/site/<int:site_id>/departements/', views_advanced.api_departements_par_site, name='api_departements_site'),
    path('api/site/<int:site_id>/stats/', views_advanced.api_statistiques_site, name='api_stats_site'),
    path('api/infos-session/', views_users.obtenir_infos_session, name='infos_session'),
    path('api/statistiques-utilisateurs/', views_users.statistiques_utilisateurs, name='statistiques_utilisateurs'),
    
    # ===== EXPORTS EXCEL =====
    path('export-excel/bulletins/', views_excel.export_bulletins_massif_excel, name='export_bulletins_excel'),
    path('export-excel/bulletin/<int:bulletin_id>/', views_excel.export_bulletin_excel, name='export_bulletin_excel'),
    path('export-excel/cnss/', views_excel.export_cnss_excel, name='export_cnss_excel'),
    path('export-excel/statistiques/', views_excel.statistiques_excel, name='statistiques_excel'),
    path('export-excel/cnss/', views_excel.page_export_cnss, name='page_export_cnss'),
    path('export-excel/cnss/<int:mois>/<int:annee>/', views_excel.export_cnss_mensuel, name='export_cnss_mensuel'),
    
    # ===== GESTION DES RUBRIQUES PERSONNALISÉES =====
    path('employe/<int:employe_id>/rubriques/', views.gestion_rubriques_employe, name='gestion_rubriques_employe'),
    path('ajax/ajouter-rubrique-ponctuelle/', views.ajouter_rubrique_ponctuelle, name='ajouter_rubrique_ponctuelle'),
    path('assignation/<int:assignation_id>/modifier/', views.modifier_assignation_rubrique, name='modifier_assignation_rubrique'),
    path('assignation/<int:assignation_id>/supprimer/', views.supprimer_assignation_rubrique, name='supprimer_assignation_rubrique'),
    path('rubriques/assignation-massive/', views.assignation_massive_rubriques, name='assignation_massive_rubriques'),
    path('admin/dashboard-rubriques/', views.dashboard_rubriques_admin, name='dashboard_rubriques_admin'),
    
    # ===== PAGES UTILITAIRES =====
    path('aide/', views.page_aide, name='aide'),
    path('deconnexion/', views.deconnexion_vue, name='deconnexion'),
    path('connexion/', views.connexion_personnalisee, name='connexion_personnalisee'),
    path('creer-comptes/', views.creer_compte_employe, name='creer_comptes'),
]