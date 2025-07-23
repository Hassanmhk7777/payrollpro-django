from django.contrib import admin
from .models import Employe, ParametrePaie, ElementPaie, Absence, BulletinPaie
from .models import ProfilUtilisateur


@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    """Interface d'administration pour les employés"""
    
    # Colonnes à afficher dans la liste
    list_display = [
        'matricule', 
        'nom', 
        'prenom', 
        'fonction', 
        'salaire_base', 
        'date_embauche',
        'situation_familiale',
        'actif'
    ]
    
    # Filtres sur le côté droit
    list_filter = [
        'actif',
        'fonction', 
        'situation_familiale',
        'date_embauche'
    ]
    
    # Barre de recherche
    search_fields = [
        'matricule', 
        'nom', 
        'prenom', 
        'cin',
        'fonction'
    ]
    
    # Champs modifiables directement dans la liste
    list_editable = ['actif']
    
    # Organisation des champs dans le formulaire de détail
    fieldsets = (
        ('Informations de base', {
            'fields': ('matricule', 'nom', 'prenom', 'cin')
        }),
        ('Informations professionnelles', {
            'fields': ('fonction', 'date_embauche', 'salaire_base', 'actif'),
            'classes': ('wide',)
        }),
        ('Informations personnelles', {
            'fields': ('situation_familiale', 'nombre_enfants'),
            'classes': ('collapse',)
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'email', 'adresse'),
            'classes': ('collapse',)
        }),
        ('Informations bancaires', {
            'fields': ('banque', 'numero_compte'),
            'classes': ('collapse',)
        }),
    )
    
    # Tri par défaut
    ordering = ['matricule']
    
    # Nombre d'éléments par page
    list_per_page = 25


@admin.register(ParametrePaie)
class ParametrePaieAdmin(admin.ModelAdmin):
    """Interface d'administration pour les paramètres de paie"""
    
    list_display = [
        'code',
        'nom', 
        'valeur_numerique',
        'valeur_pourcentage',
        'actif',
        'date_debut',
        'date_fin'
    ]
    
    list_filter = ['actif', 'date_debut']
    search_fields = ['code', 'nom']
    list_editable = ['actif']
    
    fieldsets = (
        ('Identification', {
            'fields': ('nom', 'code', 'description')
        }),
        ('Valeurs', {
            'fields': ('valeur_numerique', 'valeur_pourcentage', 'valeur_texte'),
            'description': 'Remplissez au moins une valeur selon le type de paramètre'
        }),
        ('Période de validité', {
            'fields': ('actif', 'date_debut', 'date_fin')
        }),
    )


@admin.register(ElementPaie)
class ElementPaieAdmin(admin.ModelAdmin):
    """Interface d'administration pour les éléments de paie"""
    
    list_display = [
        'employe',
        'type_element',
        'nom',
        'montant',
        'date_application',
        'recurrent'
    ]
    
    list_filter = [
        'type_element',
        'recurrent',
        'mois_application',
        'annee_application'
    ]
    
    search_fields = [
        'employe__nom',
        'employe__prenom', 
        'employe__matricule',
        'nom'
    ]
    
    # Autocomplete pour l'employé
    autocomplete_fields = ['employe']
    
    # Grouper par employé
    list_select_related = ['employe']
    
    fieldsets = (
        ('Employé et type', {
            'fields': ('employe', 'type_element', 'nom')
        }),
        ('Montant et période', {
            'fields': ('montant', 'date_application', 'mois_application', 'annee_application')
        }),
        ('Options', {
            'fields': ('recurrent', 'note')
        }),
    )
    
    # Tri par défaut
    ordering = ['-date_application', 'employe__nom']


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    """Interface d'administration pour les absences"""
    
    list_display = [
        'employe',
        'type_absence',
        'date_debut',
        'date_fin',
        'nombre_jours',
        'statut',
        'impact_salaire'
    ]
    
    list_filter = [
        'type_absence',
        'statut',
        'impact_salaire',
        'date_debut'
    ]
    
    search_fields = [
        'employe__nom',
        'employe__prenom',
        'employe__matricule'
    ]
    
    # Autocomplete pour l'employé
    autocomplete_fields = ['employe', 'approuve_par']
    
    # Champs en lecture seule
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Employé et type d\'absence', {
            'fields': ('employe', 'type_absence')
        }),
        ('Période d\'absence', {
            'fields': ('date_debut', 'date_fin', 'nombre_jours')
        }),
        ('Validation', {
            'fields': ('statut', 'approuve_par', 'date_approbation')
        }),
        ('Détails', {
            'fields': ('motif', 'note_rh', 'impact_salaire'),
            'classes': ('collapse',)
        }),
        ('Informations système', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    # Actions personnalisées
    actions = ['approuver_absences', 'refuser_absences']
    
    def approuver_absences(self, request, queryset):
        """Approuver les absences sélectionnées"""
        updated = queryset.update(statut='APPROUVE', approuve_par=request.user)
        self.message_user(request, f'{updated} absence(s) approuvée(s).')
    approuver_absences.short_description = "Approuver les absences sélectionnées"
    
    def refuser_absences(self, request, queryset):
        """Refuser les absences sélectionnées"""
        updated = queryset.update(statut='REFUSE', approuve_par=request.user)
        self.message_user(request, f'{updated} absence(s) refusée(s).')
    refuser_absences.short_description = "Refuser les absences sélectionnées"


@admin.register(BulletinPaie)
class BulletinPaieAdmin(admin.ModelAdmin):
    """Interface d'administration pour les bulletins de paie"""
    
    list_display = [
        'employe',
        'periode_formatted',
        'salaire_base',
        'salaire_brut_imposable',
        'salaire_net',
        'valide',
        'envoye'
    ]
    
    list_filter = [
        'annee',
        'mois',
        'valide',
        'envoye'
    ]
    
    search_fields = [
        'employe__nom',
        'employe__prenom',
        'employe__matricule'
    ]
    
    # Autocomplete pour l'employé
    autocomplete_fields = ['employe', 'calcule_par']
    
    # Champs en lecture seule
    readonly_fields = ['date_calcul', 'date_envoi']
    
    fieldsets = (
        ('Employé et période', {
            'fields': ('employe', 'mois', 'annee')
        }),
        ('Salaire de base', {
            'fields': (
                'salaire_base', 
                'heures_travaillees', 
                'heures_supplementaires'
            )
        }),
        ('Éléments de paie', {
            'fields': (
                'total_primes',
                'total_retenues', 
                'total_avances'
            ),
            'classes': ('wide',)
        }),
        ('Salaires bruts', {
            'fields': (
                'salaire_brut_imposable',
                'salaire_brut_non_imposable'
            )
        }),
        ('Cotisations sociales', {
            'fields': (
                'cotisation_cnss',
                'cotisation_amo',
                'cotisation_cimr'
            )
        }),
        ('Impôts', {
            'fields': ('impot_revenu',)
        }),
        ('Résultat final', {
            'fields': ('salaire_net', 'net_a_payer'),
            'classes': ('wide',)
        }),
        ('Validation et envoi', {
            'fields': (
                'valide',
                'envoye',
                'calcule_par',
                'date_calcul',
                'date_envoi'
            ),
            'classes': ('collapse',)
        }),
    )
    
    # Tri par défaut
    ordering = ['-annee', '-mois', 'employe__nom']
    
    # Actions personnalisées
    actions = ['valider_bulletins', 'marquer_envoyes']
    
    def valider_bulletins(self, request, queryset):
        """Valider les bulletins sélectionnés"""
        updated = queryset.update(valide=True)
        self.message_user(request, f'{updated} bulletin(s) validé(s).')
    valider_bulletins.short_description = "Valider les bulletins sélectionnés"
    
    def marquer_envoyes(self, request, queryset):
        """Marquer les bulletins comme envoyés"""
        from django.utils import timezone
        updated = queryset.update(envoye=True, date_envoi=timezone.now())
        self.message_user(request, f'{updated} bulletin(s) marqué(s) comme envoyé(s).')
    marquer_envoyes.short_description = "Marquer comme envoyés"


# Configuration globale de l'admin
admin.site.site_header = "Administration Système de Paie"
admin.site.site_title = "Paie Admin"
admin.site.index_title = "Gestion de la Paie - Tableau de bord"

@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'actif', 'date_creation']