from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Employe(models.Model):
    """Modèle pour les employés de l'entreprise"""
    
    # Informations personnelles
    matricule = models.CharField(max_length=10, unique=True, help_text="Ex: S001, S002...")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cin = models.CharField(max_length=20, unique=True, help_text="Carte d'identité nationale")
    
    # Informations professionnelles
    fonction = models.CharField(max_length=100, help_text="Ex: Technicien, Comptable...")
    date_embauche = models.DateField()
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, help_text="Salaire mensuel de base en DH")
    
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
