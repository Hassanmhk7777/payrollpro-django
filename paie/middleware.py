"""
Middleware pour la redirection automatique selon le rôle utilisateur
"""
from django.shortcuts import redirect
from django.urls import reverse
from .user_management import obtenir_role_utilisateur


class RoleBasedRedirectMiddleware:
    """
    Middleware qui redirige automatiquement les utilisateurs selon leur rôle
    après connexion
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs qui déclenchent une redirection automatique
        self.redirect_urls = [
            '/admin/login/',
            '/login/',
            '/',  # Accueil seulement si pas de dashboard spécifique
        ]
        
        # Mapping rôle → dashboard
        self.role_dashboards = {
            'admin': '/dashboard/admin/',
            'rh': '/dashboard/rh/',
            'employe': '/dashboard/employe/',
        }

    def __call__(self, request):
        response = self.get_response(request)
        
        # CORRECTION: Vérifier que l'attribut user existe et est authentifié
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
            
        # Vérifier si on est sur une URL qui nécessite redirection
        if request.path in self.redirect_urls:
            try:
                role = obtenir_role_utilisateur(request.user)
                
                # Obtenir le dashboard approprié
                dashboard_url = self.role_dashboards.get(role)
                
                if dashboard_url and request.path != dashboard_url:
                    return redirect(dashboard_url)
            except Exception:
                # En cas d'erreur, continuer normalement
                pass
        
        return response


class ActiveUserOnlyMiddleware:
    """
    Middleware qui déconnecte automatiquement les utilisateurs inactifs
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs exemptées de la vérification
        self.exempt_urls = [
            '/admin/login/',
            '/login/',
            '/deconnexion/',
            '/admin/logout/',
        ]

    def __call__(self, request):
        # Vérifier si l'URL est exemptée
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)
            
        # CORRECTION: Vérifier que l'attribut user existe avant de l'utiliser
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Vérifier si l'utilisateur Django est actif
            if not request.user.is_active:
                from django.contrib.auth import logout
                logout(request)
                return redirect('/login/')
                
            # Vérifier si l'employé associé est actif
            try:
                from .user_management import GestionnaireUtilisateurs
                gestionnaire = GestionnaireUtilisateurs()
                employe = gestionnaire.obtenir_employe_par_user(request.user)
                
                if employe and not employe.actif:
                    from django.contrib.auth import logout
                    logout(request)
                    return redirect('/login/')
                    
            except Exception:
                # En cas d'erreur, continuer normalement
                pass
        
        return self.get_response(request)