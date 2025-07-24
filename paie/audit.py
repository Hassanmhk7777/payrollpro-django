"""
Utilitaires pour le système d'audit automatique
"""
from functools import wraps
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import AuditLog


def audit_action(action, description_template=None, level='INFO', target_model=None):
    """
    Decorator pour auditer automatiquement les actions dans les vues
    
    Usage:
    @audit_action('CREATE', 'Création employé {employe.nom_complet}', target_model='Employe')
    def creer_employe(request):
        # Code de la vue
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Exécuter la vue
            response = view_func(request, *args, **kwargs)
            
            # Si la vue s'est bien passée (pas d'exception), logger
            try:
                # Construire la description
                if description_template:
                    # Récupérer les variables du contexte de la vue si possible
                    description = description_template.format(**kwargs)
                else:
                    description = f"Action {action} dans {view_func.__name__}"
                
                # Récupérer target_id depuis les kwargs de l'URL
                target_id = None
                if 'employe_id' in kwargs:
                    target_id = kwargs['employe_id']
                elif 'bulletin_id' in kwargs:
                    target_id = kwargs['bulletin_id']
                elif 'absence_id' in kwargs:
                    target_id = kwargs['absence_id']
                
                # Logger l'action
                AuditLog.log_action(
                    user=request.user if request.user.is_authenticated else None,
                    action=action,
                    description=description,
                    level=level,
                    target_model=target_model,
                    target_id=target_id,
                    request=request
                )
            except Exception as e:
                # En cas d'erreur de logging, ne pas faire planter la vue
                print(f"Erreur audit: {e}")
            
            return response
        return wrapper
    return decorator


def log_security_event(request, event_type, description, level='WARNING'):
    """
    Log spécifique pour les événements de sécurité
    
    Usage:
    log_security_event(request, 'ACCESS_DENIED', 'Tentative accès dashboard admin', 'WARNING')
    """
    AuditLog.log_action(
        user=request.user if request.user.is_authenticated else None,
        action='ACCESS_DENIED',
        description=f"[SÉCURITÉ] {description}",
        level=level,
        request=request,
        extra_data={
            'event_type': event_type,
            'url_attempted': request.path,
            'method': request.method
        }
    )


def log_calculation(user, calculation_type, details, request=None):
    """
    Log spécifique pour les calculs de paie
    
    Usage:
    log_calculation(request.user, 'PAIE_MENSUELLE', 'Calcul paie juin 2025 - 15 employés')
    """
    AuditLog.log_action(
        user=user,
        action='CALCULATE',
        description=f"[CALCUL] {calculation_type}: {details}",
        level='INFO',
        request=request,
        extra_data={'calculation_type': calculation_type}
    )


def log_data_change(user, model_name, object_id, change_type, description, request=None):
    """
    Log spécifique pour les modifications de données
    
    Usage:
    log_data_change(request.user, 'Employe', 123, 'UPDATE', 'Modification salaire Ahmed: 5000→5500 DH')
    """
    AuditLog.log_action(
        user=user,
        action=change_type,
        description=f"[DONNÉES] {description}",
        level='INFO',
        target_model=model_name,
        target_id=object_id,
        request=request
    )


# Signals automatiques pour connexion/déconnexion
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Signal automatique lors de la connexion"""
    from .user_management import obtenir_role_utilisateur
    
    role = obtenir_role_utilisateur(user)
    AuditLog.log_action(
        user=user,
        action='LOGIN',
        description=f"Connexion réussie - Rôle: {role}",
        level='INFO',
        request=request,
        extra_data={'role': role}
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Signal automatique lors de la déconnexion"""
    if user:  # user peut être None lors de déconnexions automatiques
        AuditLog.log_action(
            user=user,
            action='LOGOUT',
            description="Déconnexion",
            level='INFO',
            request=request
        )


class AuditMiddleware:
    """
    Middleware pour logger automatiquement les tentatives d'accès refusées
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Logger les erreurs 403 (accès refusé)
        if response.status_code == 403:
            log_security_event(
                request, 
                'ACCESS_FORBIDDEN',
                f"Accès refusé à {request.path}",
                'WARNING'
            )
        
        return response