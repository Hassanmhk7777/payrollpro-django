"""
Vues pour la gestion des utilisateurs et des comptes employés
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from .models import Employe
from .user_management import GestionnaireUtilisateurs, obtenir_role_utilisateur


def est_admin_ou_rh(user):
    """Vérifie si l'utilisateur est admin ou RH"""
    if user.is_superuser:
        return True
    
    gestionnaire = GestionnaireUtilisateurs()
    employe = gestionnaire.obtenir_employe_par_user(user)
    return employe and employe.est_rh()


@login_required
@user_passes_test(est_admin_ou_rh)
def gestion_utilisateurs(request):
    """
    Page de gestion des utilisateurs pour les admin et RH
    """
    gestionnaire = GestionnaireUtilisateurs()
    
    # Paramètres de filtrage et recherche
    recherche = request.GET.get('recherche', '')
    statut_filtre = request.GET.get('statut', 'tous')
    role_filtre = request.GET.get('role', 'tous')
    
    # Récupérer tous les employés avec filtres
    employes_query = Employe.objects.all().select_related('user').order_by('matricule')
    
    # Appliquer la recherche
    if recherche:
        employes_query = employes_query.filter(
            Q(nom__icontains=recherche) | 
            Q(prenom__icontains=recherche) | 
            Q(matricule__icontains=recherche) |
            Q(email__icontains=recherche)
        )
    
    # Filtre par statut
    if statut_filtre == 'actifs':
        employes_query = employes_query.filter(actif=True, user__is_active=True)
    elif statut_filtre == 'inactifs':
        employes_query = employes_query.filter(Q(actif=False) | Q(user__is_active=False))
    
    # Filtre par rôle
    if role_filtre == 'employe':
        employes_query = employes_query.filter(role_systeme='EMPLOYE')
    elif role_filtre == 'rh':
        employes_query = employes_query.filter(role_systeme='RH')
    
    # Séparer les employés avec et sans compte
    employes = employes_query.all()
    employes_avec_compte = [e for e in employes if e.user]
    employes_sans_compte = [e for e in employes if not e.user]
    
    # Statistiques
    stats = {
        'total_employes': Employe.objects.count(),
        'avec_compte': Employe.objects.filter(user__isnull=False).count(),
        'sans_compte': Employe.objects.filter(user__isnull=True).count(),
        'role_rh': Employe.objects.filter(role_systeme='RH').count(),
        'role_employe': Employe.objects.filter(role_systeme='EMPLOYE').count(),
        'comptes_actifs': Employe.objects.filter(user__isnull=False, user__is_active=True, actif=True).count(),
        'comptes_inactifs': Employe.objects.filter(Q(user__is_active=False) | Q(actif=False)).count(),
    }
    
    # Alertes système
    alertes = []
    if stats['sans_compte'] > 0:
        alertes.append({
            'type': 'warning',
            'message': f"{stats['sans_compte']} employé(s) sans compte d'accès",
        })
    
    if stats['comptes_inactifs'] > 0:
        alertes.append({
            'type': 'info',
            'message': f"{stats['comptes_inactifs']} compte(s) inactif(s)",
        })
    
    context = {
        'employes_avec_compte': employes_avec_compte,
        'employes_sans_compte': employes_sans_compte,
        'stats': stats,
        'alertes': alertes,
        'user_role': obtenir_role_utilisateur(request.user),
        'recherche': recherche,
        'statut_filtre': statut_filtre,
        'role_filtre': role_filtre,
        'peut_creer_rh': request.user.is_superuser,
    }
    
    return render(request, 'paie/gestion_utilisateurs.html', context)


@login_required
@user_passes_test(est_admin_ou_rh)
@require_http_methods(["GET", "POST"])
def creer_compte_employe(request, employe_id):
    """
    Crée un compte utilisateur pour un employé
    """
    employe = get_object_or_404(Employe, id=employe_id)
    gestionnaire = GestionnaireUtilisateurs()
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Vérifier si l'employé a déjà un compte
                if employe.user:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Cet employé a déjà un compte utilisateur'
                    })
                
                # Récupérer les données du formulaire
                est_rh = request.POST.get('est_rh') == 'on'
                mot_de_passe_custom = request.POST.get('mot_de_passe', '').strip()
                
                # Seuls les admin peuvent créer des comptes RH
                if est_rh and not request.user.is_superuser:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Seuls les administrateurs peuvent créer des comptes RH'
                    })
                
                # Validation du mot de passe personnalisé
                if mot_de_passe_custom and len(mot_de_passe_custom) < 6:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Le mot de passe doit contenir au moins 6 caractères'
                    })
                
                # Créer le compte
                resultat = gestionnaire.creer_compte_employe(
                    employe=employe,
                    mot_de_passe=mot_de_passe_custom if mot_de_passe_custom else None,
                    est_rh=est_rh
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Compte créé avec succès pour {employe.nom_complet()}',
                    'username': resultat['username'],
                    'mot_de_passe': resultat['mot_de_passe'],
                    'role': 'RH' if est_rh else 'Employé',
                    'user_id': resultat['user'].id
                })
                
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Erreur inattendue: {str(e)}'})
    
    # Si GET, retourner les infos de l'employé pour le modal
    return JsonResponse({
        'employe': {
            'id': employe.id,
            'nom_complet': employe.nom_complet(),
            'matricule': employe.matricule,
            'email': employe.email or '',
            'fonction': employe.fonction,
            'date_embauche': employe.date_embauche.strftime('%d/%m/%Y'),
            'mot_de_passe_suggere': GestionnaireUtilisateurs().generer_mot_de_passe_temporaire(employe)
        }
    })


@login_required
@user_passes_test(lambda u: u.is_superuser)  # Seuls les admin
@require_http_methods(["POST"])
def modifier_role_employe(request, employe_id):
    """
    Modifie le rôle d'un employé (seuls les admin)
    """
    employe = get_object_or_404(Employe, id=employe_id)
    gestionnaire = GestionnaireUtilisateurs()
    
    try:
        # Vérifier que l'employé a un compte
        if not employe.user:
            return JsonResponse({
                'success': False, 
                'error': 'Cet employé n\'a pas de compte utilisateur'
            })
        
        nouveau_role = request.POST.get('nouveau_role')
        ancien_role = employe.role_systeme
        
        if nouveau_role not in ['RH', 'EMPLOYE']:
            return JsonResponse({'success': False, 'error': 'Rôle invalide'})
        
        if nouveau_role == ancien_role:
            return JsonResponse({
                'success': False, 
                'error': f'L\'employé a déjà le rôle {employe.get_role_systeme_display()}'
            })
        
        # Empêcher la modification de son propre rôle
        if employe.user == request.user:
            return JsonResponse({
                'success': False, 
                'error': 'Vous ne pouvez pas modifier votre propre rôle'
            })
        
        with transaction.atomic():
            if nouveau_role == 'RH':
                gestionnaire.promouvoir_vers_rh(employe)
                action_msg = 'promu au rôle RH'
            else:
                gestionnaire.retrograder_de_rh(employe)
                action_msg = 'rétrogradé au rôle Employé'
            
            return JsonResponse({
                'success': True,
                'message': f'{employe.nom_complet()} a été {action_msg}',
                'nouveau_role': employe.get_role_systeme_display(),
                'ancien_role': dict(Employe.ROLE_CHOICES)[ancien_role]
            })
            
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur inattendue: {str(e)}'})


@login_required
@user_passes_test(est_admin_ou_rh)
@require_http_methods(["POST"])
def desactiver_compte(request, employe_id):
    """
    Désactive le compte d'un employé
    """
    employe = get_object_or_404(Employe, id=employe_id)
    gestionnaire = GestionnaireUtilisateurs()
    
    try:
        # Vérifications de sécurité
        if not employe.user:
            return JsonResponse({
                'success': False, 
                'error': 'Cet employé n\'a pas de compte utilisateur'
            })
        
        if employe.user == request.user:
            return JsonResponse({
                'success': False, 
                'error': 'Vous ne pouvez pas désactiver votre propre compte'
            })
        
        # Vérifier si le compte est déjà inactif
        if not employe.user.is_active or not employe.actif:
            return JsonResponse({
                'success': False, 
                'error': 'Ce compte est déjà inactif'
            })
        
        with transaction.atomic():
            gestionnaire.desactiver_compte(employe)
            
            return JsonResponse({
                'success': True,
                'message': f'Compte de {employe.nom_complet()} désactivé avec succès'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur inattendue: {str(e)}'})


@login_required
@user_passes_test(est_admin_ou_rh)
@require_http_methods(["POST"])
def reactiver_compte(request, employe_id):
    """
    Réactive le compte d'un employé
    """
    employe = get_object_or_404(Employe, id=employe_id)
    gestionnaire = GestionnaireUtilisateurs()
    
    try:
        if not employe.user:
            return JsonResponse({
                'success': False, 
                'error': 'Cet employé n\'a pas de compte utilisateur'
            })
        
        # Vérifier si le compte est déjà actif
        if employe.user.is_active and employe.actif:
            return JsonResponse({
                'success': False, 
                'error': 'Ce compte est déjà actif'
            })
        
        with transaction.atomic():
            gestionnaire.reactiver_compte(employe)
            
            return JsonResponse({
                'success': True,
                'message': f'Compte de {employe.nom_complet()} réactivé avec succès'
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur inattendue: {str(e)}'})


@login_required
@user_passes_test(est_admin_ou_rh)
@require_http_methods(["POST"])
def reinitialiser_mot_de_passe(request, employe_id):
    """
    Réinitialise le mot de passe d'un employé
    """
    employe = get_object_or_404(Employe, id=employe_id)
    gestionnaire = GestionnaireUtilisateurs()
    
    try:
        if not employe.user:
            return JsonResponse({
                'success': False, 
                'error': 'Cet employé n\'a pas de compte utilisateur'
            })
        
        # Générer un nouveau mot de passe ou utiliser celui fourni
        nouveau_mot_de_passe_custom = request.POST.get('nouveau_mot_de_passe', '').strip()
        
        if nouveau_mot_de_passe_custom:
            if len(nouveau_mot_de_passe_custom) < 6:
                return JsonResponse({
                    'success': False, 
                    'error': 'Le mot de passe doit contenir au moins 6 caractères'
                })
            nouveau_mot_de_passe = nouveau_mot_de_passe_custom
        else:
            nouveau_mot_de_passe = gestionnaire.generer_mot_de_passe_temporaire(employe)
        
        with transaction.atomic():
            # Changer le mot de passe
            employe.user.set_password(nouveau_mot_de_passe)
            employe.user.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Mot de passe réinitialisé pour {employe.nom_complet()}',
                'nouveau_mot_de_passe': nouveau_mot_de_passe,
                'username': employe.user.username
            })
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur inattendue: {str(e)}'})


@login_required
def obtenir_infos_session(request):
    """
    Retourne les informations de l'utilisateur connecté et son rôle
    """
    gestionnaire = GestionnaireUtilisateurs()
    employe = gestionnaire.obtenir_employe_par_user(request.user)
    
    # Informations de base
    infos = {
        'username': request.user.username,
        'nom_complet': f"{request.user.first_name} {request.user.last_name}".strip(),
        'email': request.user.email,
        'is_superuser': request.user.is_superuser,
        'role': obtenir_role_utilisateur(request.user),
        'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
        'date_joined': request.user.date_joined.isoformat(),
        'employe': None,
        'permissions': []
    }
    
    # Informations de l'employé associé
    if employe:
        infos['employe'] = {
            'id': employe.id,
            'matricule': employe.matricule,
            'nom_complet': employe.nom_complet(),
            'fonction': employe.fonction,
            'role_systeme': employe.get_role_systeme_display(),
            'peut_gerer_employes': employe.peut_gerer_employes(),
            'actif': employe.actif,
            'date_embauche': employe.date_embauche.isoformat(),
            'salaire_base': float(employe.salaire_base)
        }
    
    # Permissions de l'utilisateur
    permissions = []
    if request.user.is_superuser:
        permissions = ['all']
    else:
        if gestionnaire.verifier_permissions(request.user, 'gerer_employes'):
            permissions.append('gerer_employes')
        if gestionnaire.verifier_permissions(request.user, 'calculer_paie'):
            permissions.append('calculer_paie')
        if gestionnaire.verifier_permissions(request.user, 'valider_absences'):
            permissions.append('valider_absences')
        if gestionnaire.verifier_permissions(request.user, 'voir_bulletins_tous'):
            permissions.append('voir_bulletins_tous')
    
    infos['permissions'] = permissions
    
    return JsonResponse(infos)


@login_required
@user_passes_test(est_admin_ou_rh)
def statistiques_utilisateurs(request):
    """
    Retourne les statistiques détaillées des utilisateurs
    """
    # Statistiques générales
    total_employes = Employe.objects.count()
    avec_compte = Employe.objects.filter(user__isnull=False).count()
    sans_compte = total_employes - avec_compte
    
    # Comptes actifs/inactifs
    comptes_actifs = Employe.objects.filter(
        user__isnull=False, 
        user__is_active=True, 
        actif=True
    ).count()
    comptes_inactifs = avec_compte - comptes_actifs
    
    # Répartition par rôle
    admins = User.objects.filter(is_superuser=True).count()
    rh = Employe.objects.filter(role_systeme='RH').count()
    employes = Employe.objects.filter(role_systeme='EMPLOYE').count()
    
    # Connexions récentes (7 derniers jours)
    from datetime import timedelta
    
    semaine_passee = timezone.now() - timedelta(days=7)
    connexions_recentes = User.objects.filter(
        last_login__gte=semaine_passee
    ).count()
    
    # Comptes jamais utilisés
    jamais_connectes = User.objects.filter(
        last_login__isnull=True,
        employe__isnull=False
    ).count()
    
    # Nouveaux comptes cette semaine
    nouveaux_comptes = User.objects.filter(
        date_joined__gte=semaine_passee,
        employe__isnull=False
    ).count()
    
    # Top 5 des dernières connexions
    dernieres_connexions = User.objects.filter(
        last_login__isnull=False,
        employe__isnull=False
    ).select_related('employe').order_by('-last_login')[:5]
    
    stats = {
        'resume': {
            'total_employes': total_employes,
            'avec_compte': avec_compte,
            'sans_compte': sans_compte,
            'pourcentage_avec_compte': round((avec_compte / total_employes * 100) if total_employes > 0 else 0, 1)
        },
        'statuts': {
            'comptes_actifs': comptes_actifs,
            'comptes_inactifs': comptes_inactifs,
            'jamais_connectes': jamais_connectes
        },
        'roles': {
            'admins': admins,
            'rh': rh,
            'employes': employes
        },
        'activite': {
            'connexions_recentes': connexions_recentes,
            'nouveaux_comptes': nouveaux_comptes,
            'dernieres_connexions': [
                {
                    'username': user.username,
                    'nom_complet': user.employe.nom_complet() if hasattr(user, 'employe') else user.get_full_name(),
                    'last_login': user.last_login.isoformat(),
                    'role': user.employe.get_role_systeme_display() if hasattr(user, 'employe') else 'Admin'
                }
                for user in dernieres_connexions
            ]
        },
        'genere_le': timezone.now().isoformat()
    }
    
    return JsonResponse(stats)