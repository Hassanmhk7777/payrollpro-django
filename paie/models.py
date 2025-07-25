from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

# AJOUTER CES MODÈLES AVANT class Employe dans paie/models.py

class Site(models.Model):
    """
    Modèle pour gérer plusieurs sites/entreprises
    """
    # Informations de base
    nom = models.CharField(max_length=200, help_text="Nom du site/entreprise")
    code = models.CharField(max_length=20, unique=True, help_text="Code court (ex: CAS, RAB)")
    
    # Informations légales
    raison_sociale = models.CharField(max_length=250)
    forme_juridique = models.CharField(max_length=100, default="SARL")
    numero_rc = models.CharField(max_length=50, blank=True, help_text="Numéro registre commerce")
    numero_cnss = models.CharField(max_length=50, blank=True, help_text="Numéro affiliation CNSS")
    numero_patente = models.CharField(max_length=50, blank=True)
    ice = models.CharField(max_length=20, blank=True, help_text="Identifiant Commun Entreprise")
    
    # Coordonnées
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    site_web = models.URLField(blank=True)
    
    # Paramètres RH
    directeur_general = models.CharField(max_length=200, blank=True)
    directeur_rh = models.CharField(max_length=200, blank=True)
    
    # Gestion
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    def nombre_employes(self):
        """Retourne le nombre total d'employés du site"""
        return sum(dept.nombre_employes() for dept in self.departements.filter(actif=True))
    
    def masse_salariale_totale(self):
        """Calcule la masse salariale totale du site"""
        total = Decimal('0')
        for dept in self.departements.filter(actif=True):
            total += dept.masse_salariale()
        return total


class Departement(models.Model):
    """
    Modèle pour gérer les départements au sein d'un site
    """
    # Relations
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='departements')
    
    # Informations de base
    nom = models.CharField(max_length=200, help_text="Nom du département")
    code = models.CharField(max_length=20, help_text="Code court (ex: IT, RH, COMPTA)")
    description = models.TextField(blank=True)
    
    # Hiérarchie
    departement_parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sous_departements',
        help_text="Département parent si hiérarchie"
    )
    
    # Management
    responsable = models.ForeignKey(
        'Employe', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='departements_geres',
        help_text="Responsable du département"
    )
    
    # Localisation
    batiment = models.CharField(max_length=100, blank=True)
    etage = models.CharField(max_length=50, blank=True)
    bureau = models.CharField(max_length=50, blank=True)
    
    # Centre de coût
    code_analytique = models.CharField(max_length=50, blank=True, help_text="Code pour comptabilité analytique")
    budget_annuel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Gestion
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"
        ordering = ['site', 'nom']
        unique_together = ['site', 'code']  # Code unique par site
    
    def __str__(self):
        return f"{self.site.code} / {self.code} - {self.nom}"
    
    def nombre_employes(self):
        """Retourne le nombre d'employés du département"""
        return self.employes.filter(actif=True).count()
    
    def masse_salariale(self):
        """Calcule la masse salariale du département"""
        employes = self.employes.filter(actif=True)
        return sum(emp.salaire_base for emp in employes)
    
    def chemin_hierarchique(self):
        """Retourne le chemin hiérarchique complet"""
        if self.departement_parent:
            return f"{self.departement_parent.chemin_hierarchique()} > {self.nom}"
        return f"{self.site.nom} > {self.nom}"
class Employe(models.Model):
    """Modèle pour les employés de l'entreprise"""
    
    # NOUVEAU: Lien avec le système d'authentification Django
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        help_text="Compte utilisateur pour l'accès au système"
    )
    
    # NOUVEAU: Relations hiérarchiques (temporairement nullable)
    site = models.ForeignKey(
        Site, 
        on_delete=models.CASCADE, 
        related_name='employes',
        null=True,  # TEMPORAIRE
        blank=True, # TEMPORAIRE
        help_text="Site d'affectation de l'employé"
    )
    departement = models.ForeignKey(
        Departement, 
        on_delete=models.CASCADE, 
        related_name='employes',
        null=True,  # TEMPORAIRE
        blank=True, # TEMPORAIRE
        help_text="Département d'affectation"
    )
    
    # NOUVEAU: Hiérarchie managériale
    manager = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='equipe',
        help_text="Manager direct de l'employé"
    )
    
    # Informations personnelles
    matricule = models.CharField(max_length=10, unique=True, help_text="Ex: S001, S002...")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cin = models.CharField(max_length=20, unique=True, help_text="Carte d'identité nationale")
    
    # Informations professionnelles
    fonction = models.CharField(max_length=100, help_text="Ex: Technicien, Comptable...")
    date_embauche = models.DateField()
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, help_text="Salaire mensuel de base en DH")
    
    # NOUVEAU: Rôle dans le système
    ROLE_CHOICES = [
        ('EMPLOYE', 'Employé'),
        ('RH', 'Ressources Humaines'),
    ]
    role_systeme = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='EMPLOYE',
        help_text="Rôle dans le système de paie"
    )
    
    # Informations personnelles complémentaires
    SITUATION_CHOICES = [
        ('C', 'Célibataire'),
        ('M', 'Marié(e)'),
        ('D', 'Divorcé(e)'),
        ('V', 'Veuf/Veuve'),
    ]
    situation_familiale = models.CharField(max_length=1, choices=SITUATION_CHOICES, default='C')
    nombre_enfants = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Coordonnées
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    
    # Informations bancaires
    banque = models.CharField(max_length=100, blank=True)
    numero_compte = models.CharField(max_length=30, blank=True)
    
    # Statut
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Employé"
        verbose_name_plural = "Employés"
        ordering = ['matricule']
    
    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenom}"
    
    def nom_complet(self):
        """Retourne le nom complet de l'employé"""
        return f"{self.nom} {self.prenom}"
    
    def nom_complet_avec_site(self):
        """Retourne le nom complet avec site et département"""
        if self.site and self.departement:
            return f"{self.nom_complet()} ({self.site.code}/{self.departement.code})"
        return self.nom_complet()
    
    def equipe_directe(self):
        """Retourne les employés en relation directe"""
        return self.equipe.filter(actif=True)
    
    def niveau_hierarchique(self):
        """Calcule le niveau hiérarchique (0 = top management)"""
        niveau = 0
        manager_actuel = self.manager
        while manager_actuel and niveau < 10:  # Protection contre boucle infinie
            niveau += 1
            manager_actuel = manager_actuel.manager
        return niveau
    
    def est_rh(self):
        """Vérifie si l'employé a le rôle RH"""
        return self.role_systeme == 'RH'
    
    def peut_gerer_employes(self):
        """Vérifie si l'employé peut gérer d'autres employés"""
        if self.user and self.user.is_superuser:
            return True
        return self.role_systeme == 'RH'
    def anciennete_en_mois(self):
        """
        Calcule l'ancienneté de l'employé en mois
        Nécessaire pour les conditions d'ancienneté des rubriques
        """
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        if not self.date_embauche:
            return 0
        
        aujourd_hui = date.today()
        delta = relativedelta(aujourd_hui, self.date_embauche)
        return delta.years * 12 + delta.months

def get_rubriques_applicables(self, mois=None, annee=None):
    """
    Retourne les rubriques personnalisées applicables à cet employé
    pour un mois/année donnés (ou le mois courant si non spécifié)
    """
    from datetime import date
    
    if mois is None or annee is None:
        aujourd_hui = date.today()
        mois = aujourd_hui.month
        annee = aujourd_hui.year
    
    date_calcul = date(annee, mois, 1)
    
    # Rubriques assignées spécifiquement à cet employé
    rubriques_assignees = self.rubriques_personnalisees.filter(
        actif=True,
        rubrique__actif=True
    ).select_related('rubrique')
    
    rubriques_valides = []
    
    for assignation in rubriques_assignees:
        # Vérifier validité de l'assignation
        if assignation.est_valide_pour_periode(date_calcul):
            # Vérifier validité de la rubrique elle-même
            if assignation.rubrique.est_valide_pour_periode(date_calcul):
                rubriques_valides.append(assignation)
    
    return rubriques_valides

def calculer_rubriques_personnalisees(self, mois, annee, salaire_base, salaire_brut):
    """
    Calcule toutes les rubriques personnalisées pour cet employé
    
    Returns:
        dict: {
            'gains': [(rubrique, montant), ...],
            'retenues': [(rubrique, montant), ...],
            'allocations': [(rubrique, montant), ...],
            'cotisations': [(rubrique, montant), ...],
            'total_gains': Decimal,
            'total_retenues': Decimal,
            'total_allocations': Decimal,
            'total_cotisations': Decimal
        }
    """
    from decimal import Decimal
    
    resultats = {
        'gains': [],
        'retenues': [],
        'allocations': [],
        'cotisations': [],
        'total_gains': Decimal('0'),
        'total_retenues': Decimal('0'),
        'total_allocations': Decimal('0'),
        'total_cotisations': Decimal('0')
    }
    
    rubriques_applicables = self.get_rubriques_applicables(mois, annee)
    
    for assignation in rubriques_applicables:
        rubrique = assignation.rubrique
        montant = assignation.calculer_montant(mois, annee, salaire_base, salaire_brut)
        
        if montant > 0:
            type_rubrique = rubrique.type_rubrique.lower()
            if type_rubrique == 'gain':
                resultats['gains'].append((rubrique, montant))
                resultats['total_gains'] += montant
            elif type_rubrique == 'retenue':
                resultats['retenues'].append((rubrique, montant))
                resultats['total_retenues'] += montant
            elif type_rubrique == 'allocation':
                resultats['allocations'].append((rubrique, montant))
                resultats['total_allocations'] += montant
            elif type_rubrique == 'cotisation':
                resultats['cotisations'].append((rubrique, montant))
                resultats['total_cotisations'] += montant
    
    return resultats
# Vos autres modèles restent identiques...
class ParametrePaie(models.Model):
    """Paramètres de calcul de la paie (barème IR, taux CNSS, etc.)"""
    
    # Identification
    nom = models.CharField(max_length=100, help_text="Ex: Barème IR 2025, Taux CNSS...")
    code = models.CharField(max_length=20, unique=True, help_text="Ex: IR_2025, CNSS_2025")
    
    # Valeurs
    valeur_numerique = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    valeur_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="En %")
    valeur_texte = models.CharField(max_length=200, blank=True)
    
    # Méta-données
    actif = models.BooleanField(default=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Paramètre de paie"
        verbose_name_plural = "Paramètres de paie"
        ordering = ['code']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"


class ElementPaie(models.Model):
    """Éléments de paie : primes, retenues, avances, etc."""
    
    TYPE_CHOICES = [
        ('PRIME', 'Prime'),
        ('RETENUE', 'Retenue'),
        ('AVANCE', 'Avance'),
        ('HEURES_SUP', 'Heures supplémentaires'),
        ('INDEMNITE', 'Indemnité'),
    ]
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='elements_paie')
    type_element = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100, help_text="Ex: Prime transport, Avance sur salaire...")
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Période d'application
    date_application = models.DateField()
    mois_application = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    annee_application = models.IntegerField()
    
    # Méta-données
    recurrent = models.BooleanField(default=False, help_text="Se répète chaque mois")
    note = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Élément de paie"
        verbose_name_plural = "Éléments de paie"
        ordering = ['-date_application']
    
    def __str__(self):
        return f"{self.employe.nom_complet()} - {self.nom} ({self.montant} DH)"


class Absence(models.Model):
    """Gestion des absences et congés"""
    
    TYPE_ABSENCE_CHOICES = [
        ('CONGE', 'Congé payé'),
        ('MALADIE', 'Congé maladie'),
        ('MATERNITE', 'Congé maternité'),
        ('SANS_SOLDE', 'Congé sans solde'),
        ('RTT', 'Récupération temps de travail'),
        ('AUTRE', 'Autre'),
    ]
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('APPROUVE', 'Approuvé'),
        ('REFUSE', 'Refusé'),
        ('ANNULE', 'Annulé'),
    ]
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='absences')
    type_absence = models.CharField(max_length=20, choices=TYPE_ABSENCE_CHOICES)
    
    # Dates
    date_debut = models.DateField()
    date_fin = models.DateField()
    nombre_jours = models.IntegerField(help_text="Nombre de jours ouvrables")
    
    # Validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    approuve_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_approbation = models.DateTimeField(null=True, blank=True)
    
    # Détails
    motif = models.TextField(blank=True)
    note_rh = models.TextField(blank=True)
    impact_salaire = models.BooleanField(default=False, help_text="Décompte du salaire")
    
    # Méta-données
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Absence"
        verbose_name_plural = "Absences"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.employe.nom_complet()} - {self.get_type_absence_display()} ({self.nombre_jours}j)"
    
    def duree_absence(self):
        """Calcule la durée en jours de l'absence"""
        delta = self.date_fin - self.date_debut
        return delta.days + 1


class BulletinPaie(models.Model):
    """Bulletins de paie mensuels"""
    
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='bulletins')
    
    # Période
    mois = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    annee = models.IntegerField()
    
    # Calculs de base
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2)
    heures_travaillees = models.IntegerField(default=191, help_text="Heures normales du mois")
    heures_supplementaires = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    # Éléments de paie
    total_primes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_retenues = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_avances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Calculs de salaire
    salaire_brut_imposable = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    salaire_brut_non_imposable = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Cotisations sociales
    cotisation_cnss = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cotisation_amo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cotisation_cimr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Impôts
    impot_revenu = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Résultat final
    salaire_net = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Métadonnées
    date_calcul = models.DateTimeField(auto_now_add=True)
    calcule_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    valide = models.BooleanField(default=False)
    envoye = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Bulletin de paie"
        verbose_name_plural = "Bulletins de paie"
        unique_together = ['employe', 'mois', 'annee']
        ordering = ['-annee', '-mois']
    
    def __str__(self):
        return f"{self.employe.nom_complet()} - {self.mois:02d}/{self.annee}"
    
    def periode_formatted(self):
        """Retourne la période formatée"""
        mois_noms = [
            '', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ]
        return f"{mois_noms[self.mois]} {self.annee}"

class ProfilUtilisateur(models.Model):
    """Profil étendu pour l'authentification multi-rôles"""
    ROLES = [
        ('ADMIN', 'Administrateur'),
        ('RH', 'Ressources Humaines'), 
        ('EMPLOYE', 'Employé')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employe = models.OneToOneField('Employe', on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLES, default='EMPLOYE')
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"
    
    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class AuditLog(models.Model):
    """
    Logs d'audit pour tracer toutes les actions importantes du système
    """
    
    # Types d'actions
    ACTION_CHOICES = [
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'), 
        ('DELETE', 'Suppression'),
        ('VIEW', 'Consultation'),
        ('CALCULATE', 'Calcul'),
        ('ACCESS_DENIED', 'Accès refusé'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    ]
    
    # Niveaux de criticité
    LEVEL_CHOICES = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('ERROR', 'Erreur'),
        ('CRITICAL', 'Critique'),
    ]
    
    # Informations de base
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Utilisateur qui a effectué l'action"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    
    # Détails de l'action
    target_model = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Modèle concerné (Employe, BulletinPaie, etc.)"
    )
    target_id = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="ID de l'objet concerné"
    )
    description = models.TextField(help_text="Description détaillée de l'action")
    
    # Contexte technique
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="Adresse IP de l'utilisateur"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Navigateur/OS de l'utilisateur"
    )
    session_key = models.CharField(
        max_length=40, 
        blank=True,
        help_text="Clé de session Django"
    )
    
    # Données supplémentaires (JSON)
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données supplémentaires en JSON"
    )
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log d'audit"
        verbose_name_plural = "Logs d'audit"
        ordering = ['-timestamp']
    
    def __str__(self):
        username = self.user.username if self.user else 'Anonyme'
        return f"{self.timestamp.strftime('%d/%m/%Y %H:%M')} - {username} - {self.get_action_display()}"
    
    @classmethod
    def log_action(cls, user, action, description, **kwargs):
        """Méthode helper pour créer facilement un log"""
        request = kwargs.pop('request', None)
        if request:
            kwargs.setdefault('ip_address', cls._get_client_ip(request))
            kwargs.setdefault('user_agent', request.META.get('HTTP_USER_AGENT', ''))
        
        return cls.objects.create(
            user=user,
            action=action,
            description=description,
            **kwargs
        )
    
    @staticmethod
    def _get_client_ip(request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 
    # 🔧 INSTRUCTIONS : Dans paie/models.py
# 📍 CHERCHER la fin de la classe AuditLog (vers ligne 350-400)
# 🎯 AJOUTER CES NOUVELLES CLASSES APRÈS la classe AuditLog :

# ÉTAPE 1 : Ajouter ces modèles dans paie/models.py
# Localisation : après la classe ElementPaie (vers ligne 400)

class RubriquePersonnalisee(models.Model):
    """
    Modèle pour les rubriques de paie personnalisées
    Permet aux administrateurs de créer des éléments de paie flexibles
    """
    
    TYPE_CHOICES = [
        ('GAIN', 'Gain/Prime'),
        ('RETENUE', 'Retenue'),
        ('ALLOCATION', 'Allocation'),
        ('COTISATION', 'Cotisation spéciale'),
    ]
    
    MODE_CALCUL_CHOICES = [
        ('FIXE', 'Montant fixe'),
        ('POURCENTAGE', 'Pourcentage du salaire'),
        ('PAR_ENFANT', 'Par enfant'),
        ('FORMULE', 'Formule personnalisée'),
    ]
    
    PERIODICITE_CHOICES = [
        ('MENSUEL', 'Mensuel'),
        ('TRIMESTRIEL', 'Trimestriel'),
        ('ANNUEL', 'Annuel'),
        ('PONCTUEL', 'Ponctuel'),
    ]
    
    # Identification
    code = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Code unique (ex: TRANSP, MUTU, ANCIENNET)"
    )
    nom = models.CharField(
        max_length=100, 
        help_text="Nom affiché sur le bulletin (ex: Prime Transport)"
    )
    description = models.TextField(blank=True)
    
    # Classification
    type_rubrique = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES,
        help_text="Type de rubrique"
    )
    ordre_affichage = models.PositiveIntegerField(
        default=100,
        help_text="Ordre d'affichage sur le bulletin (plus petit = en haut)"
    )
    
    # Mode de calcul
    mode_calcul = models.CharField(
        max_length=20,
        choices=MODE_CALCUL_CHOICES,
        help_text="Comment calculer le montant"
    )
    
    # Valeurs de calcul
    montant_fixe = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Montant fixe en DH (si mode = FIXE)"
    )
    pourcentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        help_text="Pourcentage du salaire (si mode = POURCENTAGE)"
    )
    montant_par_enfant = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Montant par enfant (si mode = PAR_ENFANT)"
    )
    formule_personnalisee = models.TextField(
        blank=True,
        help_text="Formule Python (ex: salaire_base * 0.05 if anciennete > 5 else 0)"
    )
    
    # Périodicité et conditions
    periodicite = models.CharField(
        max_length=20,
        choices=PERIODICITE_CHOICES,
        default='MENSUEL'
    )
    condition_anciennete_min = models.PositiveIntegerField(
        default=0,
        help_text="Ancienneté minimale en mois (0 = pas de condition)"
    )
    
    # Impact fiscal et social
    soumis_ir = models.BooleanField(
        default=True,
        help_text="Soumis à l'impôt sur le revenu"
    )
    soumis_cnss = models.BooleanField(
        default=True,
        help_text="Soumis aux cotisations CNSS"
    )
    soumis_amo = models.BooleanField(
        default=True,
        help_text="Soumis à l'AMO"
    )
    
    # Limites et plafonds
    plafond_mensuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Plafond mensuel (optionnel)"
    )
    plancher_mensuel = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Montant minimum (optionnel)"
    )
    
    # Gestion
    actif = models.BooleanField(default=True)
    date_debut = models.DateField(
        help_text="Date de début d'application"
    )
    date_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Date de fin d'application (optionnel)"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    cree_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Rubrique personnalisée"
        verbose_name_plural = "Rubriques personnalisées"
        ordering = ['type_rubrique', 'ordre_affichage', 'nom']
    
    def __str__(self):
        return f"{self.code} - {self.nom}"
    
    def est_valide_pour_periode(self, date_calcul):
        """Vérifie si la rubrique est valide pour une période donnée"""
        if not self.actif:
            return False
        if date_calcul < self.date_debut:
            return False
        if self.date_fin and date_calcul > self.date_fin:
            return False
        return True
    
    def calculer_montant(self, employe, mois, annee, salaire_base, salaire_brut):
        """
        Calcule le montant de la rubrique pour un employé donné
        
        Args:
            employe: Instance Employe
            mois: Mois de calcul
            annee: Année de calcul
            salaire_base: Salaire de base de l'employé
            salaire_brut: Salaire brut calculé
            
        Returns:
            Decimal: Montant calculé
        """
        from datetime import date
        from decimal import Decimal
        
        # Vérifier la validité pour la période
        date_calcul = date(annee, mois, 1)
        if not self.est_valide_pour_periode(date_calcul):
            return Decimal('0')
        
        # Vérifier l'ancienneté si requise
        if self.condition_anciennete_min > 0:
            anciennete_mois = employe.anciennete_en_mois()
            if anciennete_mois < self.condition_anciennete_min:
                return Decimal('0')
        
        montant = Decimal('0')
        
        # Calcul selon le mode
        if self.mode_calcul == 'FIXE':
            montant = self.montant_fixe
            
        elif self.mode_calcul == 'POURCENTAGE':
            montant = salaire_base * (self.pourcentage / Decimal('100'))
            
        elif self.mode_calcul == 'PAR_ENFANT':
            nombre_enfants = employe.nombre_enfants_charges or 0
            montant = self.montant_par_enfant * nombre_enfants
            
        elif self.mode_calcul == 'FORMULE' and self.formule_personnalisee:
            try:
                # Variables disponibles dans la formule
                context = {
                    'salaire_base': float(salaire_base),
                    'salaire_brut': float(salaire_brut),
                    'anciennete': employe.anciennete_en_mois(),
                    'nombre_enfants': employe.nombre_enfants_charges or 0,
                    'coefficient': employe.coefficient_salaire or 1,
                }
                
                # Évaluation sécurisée de la formule
                result = eval(self.formule_personnalisee, {"__builtins__": {}}, context)
                montant = Decimal(str(result))
            except:
                montant = Decimal('0')  # En cas d'erreur, montant = 0
        
        # Appliquer les limites
        if self.plafond_mensuel and montant > self.plafond_mensuel:
            montant = self.plafond_mensuel
        if self.plancher_mensuel and montant < self.plancher_mensuel:
            montant = self.plancher_mensuel
        
        return montant.quantize(Decimal('0.01'))


class EmployeRubrique(models.Model):
    """
    Association entre un employé et une rubrique personnalisée
    Permet d'assigner des rubriques spécifiques à certains employés
    """
    
    employe = models.ForeignKey(
        'Employe',
        on_delete=models.CASCADE,
        related_name='rubriques_personnalisees'
    )
    rubrique = models.ForeignKey(
        'RubriquePersonnalisee',
        on_delete=models.CASCADE,
        related_name='employes_assignes'
    )
    
    # Surcharge des valeurs de la rubrique pour cet employé spécifique
    montant_personnalise = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Montant spécifique pour cet employé (surcharge la règle générale)"
    )
    pourcentage_personnalise = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Pourcentage spécifique pour cet employé"
    )
    
    # Période d'application spécifique
    date_debut = models.DateField(
        help_text="Date de début pour cet employé"
    )
    date_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Date de fin pour cet employé (optionnel)"
    )
    
    # Gestion
    actif = models.BooleanField(default=True)
    commentaire = models.TextField(
        blank=True,
        help_text="Commentaire ou justification"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Assignation rubrique employé"
        verbose_name_plural = "Assignations rubriques employés"
        unique_together = ['employe', 'rubrique']
        ordering = ['employe__matricule', 'rubrique__ordre_affichage']
    
    def __str__(self):
        return f"{self.employe.matricule} - {self.rubrique.nom}"
    
    def est_valide_pour_periode(self, date_calcul):
        """Vérifie si l'assignation est valide pour une période donnée"""
        if not self.actif:
            return False
        if date_calcul < self.date_debut:
            return False
        if self.date_fin and date_calcul > self.date_fin:
            return False
        return True
    
    def calculer_montant(self, mois, annee, salaire_base, salaire_brut):
        """
        Calcule le montant en tenant compte des personnalisations
        """
        from datetime import date
        from decimal import Decimal
        
        date_calcul = date(annee, mois, 1)
        if not self.est_valide_pour_periode(date_calcul):
            return Decimal('0')
        
        # Si montant personnalisé, l'utiliser directement
        if self.montant_personnalise is not None:
            return self.montant_personnalise
        
        # Sinon, utiliser la logique de la rubrique avec personnalisations
        rubrique = self.rubrique
        
        # Créer une copie temporaire avec les valeurs personnalisées
        if self.pourcentage_personnalise is not None:
            # Sauvegarder la valeur originale
            pourcentage_original = rubrique.pourcentage
            rubrique.pourcentage = self.pourcentage_personnalise
            
            # Calculer
            montant = rubrique.calculer_montant(
                self.employe, mois, annee, salaire_base, salaire_brut
            )
            
            # Restaurer la valeur originale
            rubrique.pourcentage = pourcentage_original
            return montant
        
        # Calcul normal
        return rubrique.calculer_montant(
            self.employe, mois, annee, salaire_base, salaire_brut
        )