"""
Decorators de permissions pour sécuriser automatiquement les vues
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .user_management import obtenir_role_utilisateur


def role_required(*roles_autorises):
    """
    Decorator qui vérifie si l'utilisateur a un des rôles autorisés
    
    Usage:
    @role_required('admin', 'rh')
    def ma_vue(request):
        # Code de la vue
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Obtenir le rôle de l'utilisateur
            role_utilisateur = obtenir_role_utilisateur(request.user)
            
            # Vérifier si le rôle est autorisé
            if role_utilisateur in roles_autorises:
                return view_func(request, *args, **kwargs)
            
            # Si AJAX, retourner JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Permissions insuffisantes',
                    'required_roles': list(roles_autorises),
                    'user_role': role_utilisateur
                }, status=403)
            
            # Sinon, message d'erreur et redirection
            messages.error(request, f'Accès refusé. Rôles requis: {", ".join(roles_autorises)}')
            return redirect('paie:accueil')
        
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator pour les vues réservées aux administrateurs
    
    Usage:
    @admin_required
    def ma_vue_admin(request):
        # Code réservé admin
    """
    return role_required('admin')(view_func)


def rh_required(view_func):
    """
    Decorator pour les vues réservées aux RH et admins
    
    Usage:
    @rh_required
    def ma_vue_rh(request):
        # Code réservé RH
    """
    return role_required('admin', 'rh')(view_func)


def employe_required(view_func):
    """
    Decorator pour les vues accessibles à tous les employés connectés
    
    Usage:
    @employe_required
    def ma_vue_employe(request):
        # Code pour tous les employés
    """
    return role_required('admin', 'rh', 'employe')(view_func)


def ajax_required(view_func):
    """
    Decorator qui vérifie que la requête est en AJAX
    
    Usage:
    @ajax_required
    def ma_vue_ajax(request):
        # Code pour requêtes AJAX uniquement
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({'error': 'Requête AJAX requise'}, status=400)
        return view_func(request, *args, **kwargs)
    return wrapper


def permission_required_custom(permission_name):
    """
    Decorator qui vérifie une permission spécifique via user_management
    
    Usage:
    @permission_required_custom('gerer_employes')
    def ma_vue(request):
        # Code avec permission spécifique
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            from .user_management import GestionnaireUtilisateurs
            
            gestionnaire = GestionnaireUtilisateurs()
            if gestionnaire.verifier_permissions(request.user, permission_name):
                return view_func(request, *args, **kwargs)
            
            # Accès refusé
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': f'Permission requise: {permission_name}'
                }, status=403)
            
            messages.error(request, f'Permission requise: {permission_name}')
            return redirect('paie:accueil')
        
        return wrapper
    return decorator


class PermissionMixin:
    """
    Mixin pour les Class-Based Views avec vérification de permissions
    
    Usage:
    class MaVue(PermissionMixin, ListView):
        required_roles = ['admin', 'rh']
        model = Employe
    """
    required_roles = []
    required_permission = None
    
    def dispatch(self, request, *args, **kwargs):
        # Vérifier que l'utilisateur est connecté
        if not request.user.is_authenticated:
            return redirect('paie:accueil')
        
        # Vérifier les rôles si spécifiés
        if self.required_roles:
            role_utilisateur = obtenir_role_utilisateur(request.user)
            if role_utilisateur not in self.required_roles:
                messages.error(request, f'Accès refusé. Rôles requis: {", ".join(self.required_roles)}')
                return redirect('paie:accueil')
        
        # Vérifier la permission spécifique si spécifiée
        if self.required_permission:
            from .user_management import GestionnaireUtilisateurs
            gestionnaire = GestionnaireUtilisateurs()
            if not gestionnaire.verifier_permissions(request.user, self.required_permission):
                messages.error(request, f'Permission requise: {self.required_permission}')
                return redirect('paie:accueil')
        
        return super().dispatch(request, *args, **kwargs)


def safe_user_access(view_func):
    """
    Decorator qui s'assure qu'un employé ne peut accéder qu'à ses propres données
    
    Usage:
    @safe_user_access
    def detail_employe(request, employe_id):
        # L'employé ne peut voir que ses propres infos
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        from .user_management import GestionnaireUtilisateurs
        from .models import Employe
        
        role_utilisateur = obtenir_role_utilisateur(request.user)
        
        # Admin et RH peuvent tout voir
        if role_utilisateur in ['admin', 'rh']:
            return view_func(request, *args, **kwargs)
        
        # Pour les employés, vérifier l'accès
        if 'employe_id' in kwargs:
            employe_id = kwargs['employe_id']
            gestionnaire = GestionnaireUtilisateurs()
            employe_connecte = gestionnaire.obtenir_employe_par_user(request.user)
            
            if not employe_connecte or employe_connecte.id != int(employe_id):
                messages.error(request, 'Vous ne pouvez accéder qu\'à vos propres informations')
                return redirect('paie:dashboard_employe')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper