from django.contrib import admin
from .models import Employe, ParametrePaie, ElementPaie, Absence, BulletinPaie, ProfilUtilisateur, AuditLog
from .models import Site, Departement
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import RubriquePersonnalisee, EmployeRubrique


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
class RubriqueRapideInline(admin.TabularInline):
    """Interface rapide pour ajouter des montants à un employé"""
    model = EmployeRubrique
    extra = 1
    fields = ['rubrique', 'montant_personnalise', 'date_debut', 'date_fin', 'actif']
    
# Puis dans EmployeAdmin, ajouter :
inlines = [RubriqueRapideInline]  # Ajouter aux inlines existants
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
        return False 

@admin.register(RubriquePersonnalisee)
class RubriquePersonnaliseeAdmin(admin.ModelAdmin):
    """Interface d'administration pour les rubriques personnalisées"""
    
    list_display = [
        'code', 'nom', 'type_rubrique', 'mode_calcul', 
        'valeur_affichage', 'impact_fiscal', 'actif', 'nombre_employes'
    ]
    list_filter = [
        'type_rubrique', 'mode_calcul', 'periodicite', 
        'actif', 'soumis_ir', 'soumis_cnss'
    ]
    search_fields = ['code', 'nom', 'description']
    readonly_fields = ['date_creation', 'date_modification']
    
    fieldsets = (
        ('Identification', {
            'fields': ('code', 'nom', 'description', 'type_rubrique', 'ordre_affichage')
        }),
        ('Mode de Calcul', {
            'fields': (
                'mode_calcul', 
                'montant_fixe', 
                'pourcentage', 
                'montant_par_enfant',
                'formule_personnalisee'
            ),
            'description': 'Définir comment calculer le montant de cette rubrique'
        }),
        ('Conditions d\'Application', {
            'fields': (
                'periodicite', 
                'condition_anciennete_min',
                'date_debut', 
                'date_fin'
            )
        }),
        ('Impact Fiscal et Social', {
            'fields': ('soumis_ir', 'soumis_cnss', 'soumis_amo'),
            'description': 'Définir l\'impact sur les calculs d\'impôts et cotisations'
        }),
        ('Limites', {
            'fields': ('plafond_mensuel', 'plancher_mensuel'),
            'classes': ('collapse',)
        }),
        ('Gestion', {
            'fields': ('actif', 'cree_par', 'date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Assigner l'utilisateur créateur automatiquement"""
        if not change:  # Nouvelle création
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)
    
    def valeur_affichage(self, obj):
        """Affiche la valeur principale de calcul selon le mode"""
        if obj.mode_calcul == 'FIXE':
            return f"{obj.montant_fixe} DH"
        elif obj.mode_calcul == 'POURCENTAGE':
            return f"{obj.pourcentage}%"
        elif obj.mode_calcul == 'PAR_ENFANT':
            return f"{obj.montant_par_enfant} DH/enfant"
        elif obj.mode_calcul == 'FORMULE':
            return "Formule personnalisée"
        return "-"
    valeur_affichage.short_description = "Valeur"
    
    def impact_fiscal(self, obj):
        """Affiche l'impact fiscal sous forme d'icônes"""
        icons = []
        if obj.soumis_ir:
            icons.append('<span style="color: red;">IR</span>')
        if obj.soumis_cnss:
            icons.append('<span style="color: blue;">CNSS</span>')
        if obj.soumis_amo:
            icons.append('<span style="color: green;">AMO</span>')
        
        if not icons:
            return '<span style="color: gray;">Exonérée</span>'
        
        return mark_safe(' | '.join(icons))
    impact_fiscal.short_description = "Impact Fiscal"
    
    def nombre_employes(self, obj):
        """Affiche le nombre d'employés assignés à cette rubrique"""
        count = obj.employes_assignes.filter(actif=True).count()
        if count > 0:
            url = reverse('admin:paie_employerubrique_changelist')
            return format_html(
                '<a href="{}?rubrique__id__exact={}">{} employé(s)</a>',
                url, obj.id, count
            )
        return "0"
    nombre_employes.short_description = "Employés"
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        queryset = super().get_queryset(request)
        return queryset.select_related('cree_par').prefetch_related('employes_assignes')
    
    actions = ['dupliquer_rubriques', 'activer_rubriques', 'desactiver_rubriques']
    
    def dupliquer_rubriques(self, request, queryset):
        """Action pour dupliquer des rubriques"""
        count = 0
        for rubrique in queryset:
            nouvelle_rubrique = RubriquePersonnalisee.objects.create(
                code=f"{rubrique.code}_COPIE",
                nom=f"{rubrique.nom} (Copie)",
                description=rubrique.description,
                type_rubrique=rubrique.type_rubrique,
                mode_calcul=rubrique.mode_calcul,
                montant_fixe=rubrique.montant_fixe,
                pourcentage=rubrique.pourcentage,
                montant_par_enfant=rubrique.montant_par_enfant,
                formule_personnalisee=rubrique.formule_personnalisee,
                periodicite=rubrique.periodicite,
                condition_anciennete_min=rubrique.condition_anciennete_min,
                soumis_ir=rubrique.soumis_ir,
                soumis_cnss=rubrique.soumis_cnss,
                soumis_amo=rubrique.soumis_amo,
                plafond_mensuel=rubrique.plafond_mensuel,
                plancher_mensuel=rubrique.plancher_mensuel,
                date_debut=rubrique.date_debut,
                date_fin=rubrique.date_fin,
                actif=False,  # Désactivée par défaut
                cree_par=request.user
            )
            count += 1
        
        self.message_user(request, f"{count} rubrique(s) dupliquée(s) avec succès.")
    dupliquer_rubriques.short_description = "Dupliquer les rubriques sélectionnées"
    
    def activer_rubriques(self, request, queryset):
        """Action pour activer des rubriques"""
        updated = queryset.update(actif=True)
        self.message_user(request, f"{updated} rubrique(s) activée(s).")
    activer_rubriques.short_description = "Activer les rubriques sélectionnées"
    
    def desactiver_rubriques(self, request, queryset):
        """Action pour désactiver des rubriques"""
        updated = queryset.update(actif=False)
        self.message_user(request, f"{updated} rubrique(s) désactivée(s).")
    desactiver_rubriques.short_description = "Désactiver les rubriques sélectionnées"


@admin.register(EmployeRubrique)
class EmployeRubriqueAdmin(admin.ModelAdmin):
    """Interface d'administration pour les assignations employé-rubrique"""
    
    list_display = [
        'employe', 'rubrique', 'valeur_personnalisee', 
        'periode_application', 'actif'
    ]
    list_filter = [
        'actif', 'rubrique__type_rubrique', 'rubrique', 
        'date_debut', 'date_fin'
    ]
    search_fields = [
        'employe__matricule', 'employe__nom', 'employe__prenom',
        'rubrique__code', 'rubrique__nom'
    ]
    autocomplete_fields = ['employe', 'rubrique']
    readonly_fields = ['date_creation']
    
    fieldsets = (
        ('Assignation', {
            'fields': ('employe', 'rubrique')
        }),
        ('Personnalisation (Optionnel)', {
            'fields': (
                'montant_personnalise', 
                'pourcentage_personnalise'
            ),
            'description': 'Surcharger les valeurs par défaut de la rubrique pour cet employé'
        }),
        ('Période d\'Application', {
            'fields': ('date_debut', 'date_fin')
        }),
        ('Gestion', {
            'fields': ('actif', 'commentaire', 'cree_par', 'date_creation'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Assigner l'utilisateur créateur automatiquement"""
        if not change:
            obj.cree_par = request.user
        super().save_model(request, obj, form, change)
    
    def valeur_personnalisee(self, obj):
        """Affiche si des valeurs sont personnalisées"""
        if obj.montant_personnalise is not None:
            return f"{obj.montant_personnalise} DH (fixe)"
        elif obj.pourcentage_personnalise is not None:
            return f"{obj.pourcentage_personnalise}% (pers.)"
        else:
            return "Valeur standard"
    valeur_personnalisee.short_description = "Valeur"
    
    def periode_application(self, obj):
        """Affiche la période d'application"""
        if obj.date_fin:
            return f"{obj.date_debut} → {obj.date_fin}"
        else:
            return f"Depuis le {obj.date_debut}"
    periode_application.short_description = "Période"
    
    def get_queryset(self, request):
        """Optimiser les requêtes"""
        queryset = super().get_queryset(request)
        return queryset.select_related('employe', 'rubrique', 'cree_par')


# Optionnel : Intégrer dans l'admin des employés
class EmployeRubriqueInline(admin.TabularInline):
    """Inline pour gérer les rubriques directement depuis la fiche employé"""
    model = EmployeRubrique
    extra = 0
    autocomplete_fields = ['rubrique']
    fields = [
        'rubrique', 'montant_personnalise', 'pourcentage_personnalise',
        'date_debut', 'date_fin', 'actif'
    ]
    
    def get_queryset(self, request):
        """Afficher seulement les rubriques actives par défaut"""
        queryset = super().get_queryset(request)
        return queryset.select_related('rubrique').filter(actif=True)
