from django.contrib import admin
from .models import Employe, ParametrePaie, ElementPaie, Absence, BulletinPaie, ProfilUtilisateur, AuditLog, RubriquePersonnalisee, EmployeRubrique 
from .models import ProfilUtilisateur
from .models import Site, Departement


# AJOUTER CES IMPORTS en haut du fichier paie/admin.py (après les imports existants)
from .models import Site, Departement

# AJOUTER CES CLASSES ADMIN AVANT @admin.register(Employe)

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    """Interface d'administration pour les sites"""
    
    list_display = [
        'code',
        'nom', 
        'ville',
        'nombre_employes_display',
        'masse_salariale_display',
        'actif'
    ]
    
    list_filter = ['actif', 'ville', 'forme_juridique']
    search_fields = ['nom', 'code', 'raison_sociale', 'ville']
    list_editable = ['actif']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code', 'actif')
        }),
        ('Informations légales', {
            'fields': (
                'raison_sociale', 
                'forme_juridique',
                'numero_rc',
                'numero_cnss', 
                'numero_patente',
                'ice'
            ),
            'classes': ('collapse',)
        }),
        ('Coordonnées', {
            'fields': (
                'adresse',
                'ville', 
                'code_postal',
                'telephone',
                'email',
                'site_web'
            )
        }),
        ('Management', {
            'fields': ('directeur_general', 'directeur_rh'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_employes_display(self, obj):
        return obj.nombre_employes()
    nombre_employes_display.short_description = 'Employés'
    
    def masse_salariale_display(self, obj):
        return f"{obj.masse_salariale_totale():,.0f} DH"
    masse_salariale_display.short_description = 'Masse Salariale'


@admin.register(Departement)
class DepartementAdmin(admin.ModelAdmin):
    """Interface d'administration pour les départements"""
    
    list_display = [
        'code',
        'nom',
        'site',
        'departement_parent',
        'responsable',
        'nombre_employes_display',
        'actif'
    ]
    
    list_filter = ['site', 'actif', 'departement_parent']
    search_fields = ['nom', 'code', 'site__nom', 'description']
    list_editable = ['actif']
    
    # Autocomplete pour les relations
    autocomplete_fields = ['site', 'departement_parent', 'responsable']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('site', 'nom', 'code', 'description', 'actif')
        }),
        ('Hiérarchie', {
            'fields': ('departement_parent', 'responsable')
        }),
        ('Localisation', {
            'fields': ('batiment', 'etage', 'bureau'),
            'classes': ('collapse',)
        }),
        ('Gestion financière', {
            'fields': ('code_analytique', 'budget_annuel'),
            'classes': ('collapse',)
        }),
    )
    
    def nombre_employes_display(self, obj):
        return obj.nombre_employes()
    nombre_employes_display.short_description = 'Employés'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrer les choix selon le contexte"""
        if db_field.name == "departement_parent":
            # Un département ne peut avoir comme parent que des départements du même site
            if 'site' in request.GET:
                kwargs["queryset"] = Departement.objects.filter(site_id=request.GET['site'])
            else:
                kwargs["queryset"] = Departement.objects.filter(actif=True)
        
        if db_field.name == "responsable":
            # Le responsable doit être du même site
            if 'site' in request.GET:
                kwargs["queryset"] = Employe.objects.filter(site_id=request.GET['site'], actif=True)
            else:
                kwargs["queryset"] = Employe.objects.filter(actif=True)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
# REMPLACER la classe EmployeAdmin existante par cette version :

# REMPLACER TEMPORAIREMENT la classe EmployeAdmin dans paie/admin.py par :

# REMPLACER la classe EmployeAdmin dans paie/admin.py par :

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    """Interface d'administration pour les employés - VERSION MULTI-SITES FINALE"""
    
    # Colonnes à afficher dans la liste
    list_display = [
        'matricule', 
        'nom', 
        'prenom',
        'site_display',
        'departement_display', 
        'fonction', 
        'manager_display',
        'salaire_base', 
        'date_embauche',
        'actif'
    ]
    
    # Filtres sur le côté droit
    list_filter = [
        'site',
        'departement',
        'actif',
        'fonction', 
        'role_systeme',
        'situation_familiale',
        'date_embauche'
    ]
    
    # Barre de recherche
    search_fields = [
        'matricule', 
        'nom', 
        'prenom', 
        'cin',
        'fonction',
        'site__nom',
        'departement__nom'
    ]
    
    # Champs modifiables directement dans la liste
    list_editable = ['actif']
    
    # Autocomplete pour les relations
    autocomplete_fields = ['user']
    
    # Organisation des champs dans le formulaire de détail
    fieldsets = (
        ('Affectation organisationnelle', {
            'fields': ('site', 'departement', 'manager'),
            'classes': ('wide',),
            'description': 'Définir l\'affectation hiérarchique de l\'employé'
        }),
        ('Informations de base', {
            'fields': ('matricule', 'nom', 'prenom', 'cin')
        }),
        ('Informations professionnelles', {
            'fields': ('fonction', 'date_embauche', 'salaire_base', 'actif'),
            'classes': ('wide',)
        }),
        ('Système utilisateur', {
            'fields': ('user', 'role_systeme'),
            'classes': ('collapse',)
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
    
    # Tri par défaut par hiérarchie
    ordering = ['site__nom', 'departement__nom', 'matricule']
    
    # Nombre d'éléments par page
    list_per_page = 25
    
    # Méthodes d'affichage personnalisées
    def site_display(self, obj):
        if obj.site:
            return f"{obj.site.code} - {obj.site.nom}"
        return "⚠️ Non assigné"
    site_display.short_description = 'Site'
    site_display.admin_order_field = 'site__nom'
    
    def departement_display(self, obj):
        if obj.departement:
            return f"{obj.departement.code} - {obj.departement.nom}"
        return "⚠️ Non assigné"
    departement_display.short_description = 'Département'
    departement_display.admin_order_field = 'departement__nom'
    
    def manager_display(self, obj):
        if obj.manager:
            return f"{obj.manager.nom_complet()} ({obj.manager.matricule})"
        return "—"
    manager_display.short_description = 'Manager'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrer les choix selon le contexte hiérarchique"""
        
        if db_field.name == "departement":
            # Filtrer les départements selon le site sélectionné
            if 'site' in request.GET:
                kwargs["queryset"] = Departement.objects.filter(
                    site_id=request.GET['site'], 
                    actif=True
                ).order_by('nom')
            else:
                kwargs["queryset"] = Departement.objects.filter(actif=True).order_by('site__nom', 'nom')
        
        elif db_field.name == "manager":
            # Le manager doit être du même site, idéalement du même département ou niveau supérieur
            if 'site' in request.GET:
                kwargs["queryset"] = Employe.objects.filter(
                    site_id=request.GET['site'], 
                    actif=True
                ).order_by('departement__nom', 'nom')
            else:
                kwargs["queryset"] = Employe.objects.filter(actif=True).order_by('site__nom', 'nom')
        
        elif db_field.name == "site":
            kwargs["queryset"] = Site.objects.filter(actif=True).order_by('nom')
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Actions personnalisées
    actions = ['export_par_site', 'assigner_site_departement']
    
    def export_par_site(self, request, queryset):
        """Exporter les employés par site"""
        sites = queryset.values('site__nom').distinct()
        self.message_user(request, f'Export préparé pour {sites.count()} site(s) - {queryset.count()} employé(s)')
    export_par_site.short_description = "📊 Exporter par site"
    
    def assigner_site_departement(self, request, queryset):
        """Assistant pour assigner en masse site/département"""
        employes_sans_site = queryset.filter(site__isnull=True).count()
        if employes_sans_site > 0:
            self.message_user(request, f'⚠️ {employes_sans_site} employé(s) sans site assigné', level='WARNING')
        else:
            self.message_user(request, '✅ Tous les employés sélectionnés ont un site assigné')
    assigner_site_departement.short_description = "🏢 Vérifier assignations"
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
    
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Interface d'administration pour les logs d'audit"""
    
    list_display = ['timestamp', 'user', 'action', 'level', 'description_short', 'ip_address']
    list_filter = ['action', 'level', 'timestamp', 'target_model']
    search_fields = ['user__username', 'description', 'ip_address']
    readonly_fields = ['timestamp', 'user', 'action', 'level', 'description', 'ip_address', 'target_model', 'target_id']
    date_hierarchy = 'timestamp'
    
    def description_short(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_short.short_description = 'Description'
    
    def has_add_permission(self, request):
        return False  # Pas de création manuelle
    
    def has_change_permission(self, request, obj=None):
        return False  # Pas de modification 
    # 🔧 INSTRUCTIONS : Dans paie/admin.py
# 📍 CHERCHER les imports en haut du fichier (ligne 1-5)
# 🎯 AJOUTER ces imports aux models existants :

from .models import (
    Employe, ParametrePaie, ElementPaie, Absence, BulletinPaie, ProfilUtilisateur, 
    AuditLog, RubriquePersonnalisee, EmployeRubrique  # ← AJOUTER CES DEUX
)

# 📍 PUIS CHERCHER la fin du fichier admin.py (après @admin.register(AuditLog))
# 🎯 AJOUTER CES NOUVELLES CLASSES D'ADMINISTRATION :

@admin.register(RubriquePersonnalisee)
class RubriquePersonnaliseeAdmin(admin.ModelAdmin):
    """Interface d'administration pour les rubriques personnalisées"""
    
    list_display = [
        'code',
        'nom',
        'type_rubrique',
        'mode_calcul',
        'montant_fixe',
        'pourcentage',
        'frequence',
        'actif',
        'date_debut'
    ]
    
    list_filter = [
        'type_rubrique',
        'mode_calcul',
        'frequence',
        'actif',
        'soumis_ir',
        'soumis_cnss',
        'soumis_amo'
    ]
    
    search_fields = ['code', 'nom', 'description']
    list_editable = ['actif']
    
    fieldsets = (
        ('Identification', {
            'fields': ('code', 'nom', 'description')
        }),
        ('Classification', {
            'fields': ('type_rubrique', 'mode_calcul', 'frequence')
        }),
        ('Paramètres de calcul', {
            'fields': (
                'montant_fixe',
                'pourcentage', 
                'formule_calcul'
            ),
            'description': 'Définissez le mode de calcul de la rubrique'
        }),
        ('Conditions d\'application', {
            'fields': ('salaire_minimum', 'salaire_maximum'),
            'classes': ('collapse',)
        }),
        ('Impact fiscal et social', {
            'fields': ('soumis_ir', 'soumis_cnss', 'soumis_amo'),
            'classes': ('wide',)
        }),
        ('Période de validité', {
            'fields': ('actif', 'date_debut', 'date_fin')
        }),
        ('Métadonnées', {
            'fields': ('cree_par',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['date_creation', 'date_modification']
    ordering = ['code']
    
    # Actions personnalisées
    actions = ['dupliquer_rubriques', 'activer_rubriques', 'desactiver_rubriques']
    
    def dupliquer_rubriques(self, request, queryset):
        """Dupliquer les rubriques sélectionnées"""
        count = 0
        for rubrique in queryset:
            # Créer une copie
            nouveau_code = f"{rubrique.code}_COPIE"
            if not RubriquePersonnalisee.objects.filter(code=nouveau_code).exists():
                rubrique.pk = None
                rubrique.code = nouveau_code
                rubrique.nom = f"{rubrique.nom} (Copie)"
                rubrique.actif = False
                rubrique.save()
                count += 1
        
        self.message_user(request, f'{count} rubrique(s) dupliquée(s).')
    dupliquer_rubriques.short_description = "Dupliquer les rubriques sélectionnées"
    
    def activer_rubriques(self, request, queryset):
        """Activer les rubriques sélectionnées"""
        updated = queryset.update(actif=True)
        self.message_user(request, f'{updated} rubrique(s) activée(s).')
    activer_rubriques.short_description = "Activer les rubriques sélectionnées"
    
    def desactiver_rubriques(self, request, queryset):
        """Désactiver les rubriques sélectionnées"""
        updated = queryset.update(actif=False)
        self.message_user(request, f'{updated} rubrique(s) désactivée(s).')
    desactiver_rubriques.short_description = "Désactiver les rubriques sélectionnées"
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder avec l'utilisateur créateur"""
        if not change:  # Nouvelle création
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)


class EmployeRubriqueInline(admin.TabularInline):
    """Inline pour gérer les rubriques depuis la fiche employé"""
    
    model = EmployeRubrique
    extra = 0
    fields = [
        'rubrique',
        'montant_personnalise',
        'pourcentage_personnalise', 
        'date_debut',
        'date_fin',
        'actif',
        'note'
    ]
    readonly_fields = ['date_creation']
    
    def get_queryset(self, request):
        """Afficher seulement les rubriques actives par défaut"""
        return super().get_queryset(request).select_related('rubrique')


@admin.register(EmployeRubrique)
class EmployeRubriqueAdmin(admin.ModelAdmin):
    """Interface d'administration pour les associations employé-rubrique"""
    
    list_display = [
        'employe',
        'rubrique',
        'montant_personnalise',
        'pourcentage_personnalise',
        'date_debut',
        'date_fin',
        'actif'
    ]
    
    list_filter = [
        'rubrique__type_rubrique',
        'actif',
        'date_debut',
        'employe__fonction'
    ]
    
    search_fields = [
        'employe__nom',
        'employe__prenom',
        'employe__matricule',
        'rubrique__code',
        'rubrique__nom'
    ]
    
    autocomplete_fields = ['employe', 'rubrique']
    list_editable = ['actif']
    
    fieldsets = (
        ('Association', {
            'fields': ('employe', 'rubrique')
        }),
        ('Paramètres personnalisés', {
            'fields': (
                'montant_personnalise',
                'pourcentage_personnalise'
            ),
            'description': 'Paramètres spécifiques à cet employé (écrasent le calcul par défaut)'
        }),
        ('Période et statut', {
            'fields': ('date_debut', 'date_fin', 'actif', 'note')
        }),
    )
    
    readonly_fields = ['date_creation', 'date_modification']
    ordering = ['employe__nom', 'rubrique__code']
    
    # Actions personnalisées
    actions = ['calculer_apercu_montants', 'activer_associations', 'desactiver_associations']
    
    def calculer_apercu_montants(self, request, queryset):
        """Calculer un aperçu des montants pour les associations sélectionnées"""
        resultats = []
        for association in queryset.select_related('employe', 'rubrique'):
            employe = association.employe
            montant = association.calculer_montant(employe.salaire_base, employe.salaire_base)
            resultats.append(f"{employe.nom_complet()}: {montant} DH")
        
        message = "Aperçu des montants:\n" + "\n".join(resultats[:10])
        if len(resultats) > 10:
            message += f"\n... et {len(resultats)-10} autres"
        
        self.message_user(request, message)
    calculer_apercu_montants.short_description = "Calculer aperçu des montants"
    
    def activer_associations(self, request, queryset):
        """Activer les associations sélectionnées"""
        updated = queryset.update(actif=True)
        self.message_user(request, f'{updated} association(s) activée(s).')
    activer_associations.short_description = "Activer les associations"
    
    def desactiver_associations(self, request, queryset):
        """Désactiver les associations sélectionnées"""
        updated = queryset.update(actif=False)
        self.message_user(request, f'{updated} association(s) désactivée(s).')
    desactiver_associations.short_description = "Désactiver les associations"


# 🔧 MISE À JOUR de la classe EmployeAdmin existante
# 📍 CHERCHER dans admin.py la classe EmployeAdmin (vers ligne 20-80)
# 🎯 AJOUTER cette ligne dans la liste des inlines :

# DANS LA CLASSE EmployeAdmin EXISTANTE, AJOUTER :
# inlines = [EmployeRubriqueInline]  # ← AJOUTER CETTE LIGNE