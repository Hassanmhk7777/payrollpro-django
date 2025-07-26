# gestion_paie/urls.py - VERSION CORRIGÉE SIMPLE

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

# Vue simple pour éviter la récursion
def accueil_simple(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return redirect('/login/')

def dashboard_temporaire(request):
    from django.http import HttpResponse
    if request.user.is_authenticated:
        return HttpResponse(f"""
        <h1>🎉 PayrollPro - Tableau de Bord</h1>
        <p>Bienvenue {request.user.username}!</p>
        <h2>🔗 Liens disponibles :</h2>
        <ul>
            <li><a href="/admin/">Administration Django</a></li>
            <li><a href="/logout/">Déconnexion</a></li>
        </ul>
        <h3>📊 Prochaines étapes :</h3>
        <ol>
            <li>Créer les données d'exemple</li>
            <li>Configurer les dashboards modernes</li>
            <li>Tester les fonctionnalités</li>
        </ol>
        <hr>
        <p><strong>Note :</strong> Les dashboards modernes seront activés après la correction des URLs.</p>
        """)
    else:
        return redirect('/login/')

urlpatterns = [
    # Administration Django
    path('admin/', admin.site.urls),
    
    # Pages principales (temporaires)
    path('', accueil_simple, name='accueil'),
    path('dashboard/', dashboard_temporaire, name='dashboard'),
    
    # Authentification
    path('login/', auth_views.LoginView.as_view(
        template_name='paie/connexion_simple.html',
        redirect_authenticated_user=True,
        next_page='/dashboard/'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='/login/'
    ), name='logout'),
    
    # Inclusion des URLs de l'app paie
    path('', include('paie.urls')),
]

# Configuration du titre de l'admin
admin.site.site_header = "PayrollPro Administration"
admin.site.site_title = "PayrollPro Admin"
admin.site.index_title = "Bienvenue dans l'administration PayrollPro"