"""
Système de gestion des utilisateurs et permissions pour PayrollPro
"""
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Employe


class GestionnaireUtilisateurs:
    """
    Classe pour gérer la création et l'assignation des utilisateurs
    """
    
    def __init__(self):
        # Créer les groupes s'ils n'existent pas
        self.groupe_rh, created = Group.objects.get_or_create(name='RH')
        self.groupe_employe, created = Group.objects.get_or_create(name='Employes')
    
    def generer_nom_utilisateur(self, employe):
        """
        Génère un nom d'utilisateur unique basé sur le matricule et nom
        """
        base_username = f"{employe.matricule.lower()}_{slugify(employe.nom)}"
        
        # Vérifier l'unicité
        counter = 1
        username = base_username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    def generer_mot_de_passe_temporaire(self, employe):
        """
        Génère un mot de passe temporaire
        Format: Matricule + 4 premiers caractères du nom en majuscules
        """
        return f"{employe.matricule}{employe.nom[:4].upper()}2025"
    
    def creer_compte_employe(self, employe, mot_de_passe=None, est_rh=False):
        """
        Crée un compte utilisateur pour un employé
        """
        # Vérifier que l'employé n'a pas déjà un compte
        if employe.user:
            raise ValidationError(f"L'employé {employe.nom_complet()} a déjà un compte utilisateur")
        
        # Générer les identifiants
        username = self.generer_nom_utilisateur(employe)
        if not mot_de_passe:
            mot_de_passe = self.generer_mot_de_passe_temporaire(employe)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=employe.email,
            password=mot_de_passe,
            first_name=employe.prenom,
            last_name=employe.nom
        )
        
        # Assigner le groupe approprié
        if est_rh:
            user.groups.add(self.groupe_rh)
            employe.role_systeme = 'RH'
        else:
            user.groups.add(self.groupe_employe)
            employe.role_systeme = 'EMPLOYE'
        
        # Lier l'utilisateur à l'employé
        employe.user = user
        employe.save()
        
        return {
            'user': user,
            'username': username,
            'mot_de_passe': mot_de_passe,
            'employe': employe
        }
    
    def promouvoir_vers_rh(self, employe):
        """
        Promeut un employé au rôle RH
        """
        if not employe.user:
            raise ValidationError("L'employé doit avoir un compte utilisateur")
        
        # Retirer du groupe employé et ajouter au groupe RH
        employe.user.groups.remove(self.groupe_employe)
        employe.user.groups.add(self.groupe_rh)
        
        # Mettre à jour le rôle
        employe.role_systeme = 'RH'
        employe.save()
        
        return employe
    
    def retrograder_de_rh(self, employe):
        """
        Rétrograde un employé RH vers employé normal
        """
        if not employe.user:
            raise ValidationError("L'employé doit avoir un compte utilisateur")
        
        # Retirer du groupe RH et ajouter au groupe employé
        employe.user.groups.remove(self.groupe_rh)
        employe.user.groups.add(self.groupe_employe)
        
        # Mettre à jour le rôle
        employe.role_systeme = 'EMPLOYE'
        employe.save()
        
        return employe
    
    def desactiver_compte(self, employe):
        """
        Désactive le compte d'un employé
        """
        if employe.user:
            employe.user.is_active = False
            employe.user.save()
        
        employe.actif = False
        employe.save()
    
    def reactiver_compte(self, employe):
        """
        Réactive le compte d'un employé
        """
        if employe.user:
            employe.user.is_active = True
            employe.user.save()
        
        employe.actif = True
        employe.save()
    
    def obtenir_employe_par_user(self, user):
        """
        Récupère l'employé associé à un utilisateur
        """
        try:
            return Employe.objects.get(user=user)
        except Employe.DoesNotExist:
            return None
    
    def verifier_permissions(self, user, action):
        """
        Vérifie les permissions d'un utilisateur pour une action donnée
        """
        # Les superusers peuvent tout faire
        if user.is_superuser:
            return True
        
        # Récupérer l'employé associé
        employe = self.obtenir_employe_par_user(user)
        if not employe:
            return False
        
        # Définir les permissions par action
        permissions = {
            'gerer_employes': ['superuser', 'rh'],
            'calculer_paie': ['superuser', 'rh'],
            'valider_absences': ['superuser', 'rh'],
            'voir_bulletins_tous': ['superuser', 'rh'],
            'modifier_parametres': ['superuser'],
            'voir_son_bulletin': ['superuser', 'rh', 'employe'],
            'demander_absence': ['superuser', 'rh', 'employe'],
        }
        
        roles_autorises = permissions.get(action, [])
        
        if 'superuser' in roles_autorises and user.is_superuser:
            return True
        if 'rh' in roles_autorises and employe.est_rh():
            return True
        if 'employe' in roles_autorises and employe.role_systeme == 'EMPLOYE':
            return True
        
        return False


def obtenir_role_utilisateur(user):
    """
    Fonction utilitaire pour obtenir le rôle d'un utilisateur
    """
    if user.is_superuser:
        return 'admin'
    
    gestionnaire = GestionnaireUtilisateurs()
    employe = gestionnaire.obtenir_employe_par_user(user)
    
    if employe:
        if employe.est_rh():
            return 'rh'
        else:
            return 'employe'
    
    return 'inconnu'


def peut_acceder_page(user, page):
    """
    Vérifie si un utilisateur peut accéder à une page donnée
    """
    gestionnaire = GestionnaireUtilisateurs()
    
    pages_permissions = {
        'liste_employes': 'gerer_employes',
        'calcul_paie': 'calculer_paie',
        'gestion_absences': 'valider_absences',
        'dashboard_admin': 'modifier_parametres',
        'dashboard_rh': 'calculer_paie',
        'dashboard_employe': 'voir_son_bulletin',
    }
    
    permission_requise = pages_permissions.get(page)
    if permission_requise:
        return gestionnaire.verifier_permissions(user, permission_requise)
    
    return True  # Accès libre par défaut