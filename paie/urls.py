from django.urls import path
from . import views

app_name = 'paie'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/rh/', views.dashboard_rh, name='dashboard_rh'),
    path('dashboard/employe/', views.dashboard_employe, name='dashboard_employe'),
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/<int:employe_id>/', views.detail_employe, name='detail_employe'),
    path('calcul-paie/', views.calcul_paie, name='calcul_paie'),
    path('bulletin/<int:bulletin_id>/pdf/', views.generer_bulletin_pdf, name='bulletin_pdf'),
    path('absences/', views.gestion_absences, name='gestion_absences'),
    path('absences/<int:absence_id>/valider/', views.valider_absence, name='valider_absence'),
    path('absences/validation-lot/', views.validation_lot_absences, name='validation_lot_absences'),
    path('absences/statistiques/', views.statistiques_absences, name='statistiques_absences'),
    path('calendrier-absences/', views.calendrier_absences, name='calendrier_absences'),
    path('test-absences/', views.test_calcul_absences, name='test_calcul_absences'),
    path('deconnexion/', views.deconnexion_vue, name='deconnexion'),
]