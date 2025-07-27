# Imports Django
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Avg
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_http_methods
from .models import Employe, RubriquePersonnalisee, EmployeRubrique, BulletinPaie
from .forms import RubriqueRapideForm, AssignationMassiqueForm
from decimal import Decimal
from datetime import date
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .models import Employe, RubriquePersonnalisee, EmployeRubrique
from datetime import date
import json
# Imports locaux

from .user_management import GestionnaireUtilisateurs, obtenir_role_utilisateur
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .decorators import admin_required, rh_required, employe_required, safe_user_access
# AJOUTER ces imports après la ligne "from .decorators import..."
from .audit import audit_action, log_calculation, log_data_change, log_security_event
from .models import Employe, ParametrePaie, ElementPaie, Absence, BulletinPaie, Site, Departement
def accueil(request):
    """Page d'accueil - la redirection est gérée par le middleware"""
    
    # Statistiques de base pour la page d'accueil
    total_employes = Employe.objects.filter(actif=True).count()
    absences_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
    
    # Calcul simple de la masse salariale
    employes_actifs = Employe.objects.filter(actif=True)
    masse_salariale = sum(employe.salaire_base for employe in employes_actifs)
    
    context = {
        'total_employes': total_employes,
        'absences_attente': absences_attente,
        'masse_salariale': masse_salariale,
    }
    
    return render(request, 'paie/accueil_moderne.html', context)

@login_required
def accueil_moderne(request):
    """Page d'accueil SPA moderne"""
    
    # Mêmes statistiques que la page d'accueil
    total_employes = Employe.objects.filter(actif=True).count()
    absences_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
    
    # Calcul simple de la masse salariale
    employes_actifs = Employe.objects.filter(actif=True)
    masse_salariale = sum(employe.salaire_base for employe in employes_actifs)
    
    # Nouveaux employés du mois
    from datetime import datetime, timedelta
    debut_mois = datetime.now().replace(day=1)
    nouveaux_employes = Employe.objects.filter(
        date_embauche__gte=debut_mois,
        actif=True
    ).count()
    
    context = {
        'total_employes': total_employes,
        'absences_attente': absences_attente,
        'masse_salariale': masse_salariale,
        'nouveaux_employes': nouveaux_employes,
    }
    
    return render(request, 'paie/accueil_moderne.html', context)

def connexion_personnalisee(request):
    """Connexion avec redirection selon le rôle"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirection selon le rôle
            try:
                profil = user.profilutilisateur
                if profil.role == 'ADMIN':
                    return redirect('paie:dashboard_admin')
                elif profil.role == 'RH':
                    return redirect('paie:dashboard_rh')
                else:
                    return redirect('paie:dashboard_employe')
            except:
                # Si pas de profil, redirection par défaut
                return redirect('paie:accueil')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')
    
    return render(request, 'paie/connexion_moderne.html')
@login_required
@audit_action('CREATE', 'Création compte employé {employe_id}', target_model='User')
def creer_compte_employe(request):
    """Interface simple pour créer des comptes employés - VERSION UNIFIÉE"""
    # Vérifier que c'est un admin
    if not request.user.is_superuser:
        messages.error(request, 'Accès non autorisé')
        return redirect('paie:accueil')
    
    # NOUVEAU: Utiliser le même système que views_users
    employes_sans_compte = Employe.objects.filter(user__isnull=True, actif=True)
    
    if request.method == 'POST':
        employe_id = request.POST.get('employe_id')
        role = request.POST.get('role', 'EMPLOYE')
        
        try:
            employe = Employe.objects.get(id=employe_id)
            
            # NOUVEAU: Utiliser GestionnaireUtilisateurs
            from .user_management import GestionnaireUtilisateurs
            gestionnaire = GestionnaireUtilisateurs()
            
            # Déterminer si c'est RH selon le rôle choisi
            est_rh = (role == 'RH')
            
            # Créer le compte avec le gestionnaire unifié
            resultat = gestionnaire.creer_compte_employe(
                employe=employe,
                mot_de_passe=None,  # Génération auto
                est_rh=est_rh
            )
            
            messages.success(request, 
                f'Compte créé pour {employe.nom_complet()}\n'
                f'Username: {resultat["username"]}\n'
                f'Password: {resultat["mot_de_passe"]}\n'
                f'Rôle: {employe.get_role_systeme_display()}'
            )
            return redirect('paie:gestion_utilisateurs')
        except Exception as e:
            messages.error(request, f'Erreur: {str(e)}')
    
    context = {
        'employes_sans_compte': employes_sans_compte
    }
    return render(request, 'paie/creer_comptes_moderne.html', context)
@login_required
def dashboard_admin(request):
    """Dashboard pour les administrateurs - Redirection vers SPA moderne"""
    return redirect('paie:accueil_moderne')
    total_cotisations = bulletins_mois.aggregate(
        total_cnss=Sum('cotisation_cnss'),
        total_amo=Sum('cotisation_amo'),
        total_cimr=Sum('cotisation_cimr')
    )
    total_cotisations_somme = (total_cotisations['total_cnss'] or 0) + \
                             (total_cotisations['total_amo'] or 0) + \
                             (total_cotisations['total_cimr'] or 0)
    
    # Absences en attente
    absences_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
    
    # Statistiques des comptes utilisateurs
    employes_avec_compte = Employe.objects.filter(user__isnull=False).count()
    employes_sans_compte = Employe.objects.filter(user__isnull=True).count()
    
    # Alertes
    alertes = []
    if absences_attente > 0:
        alertes.append(f"{absences_attente} demande(s) d'absence en attente de validation")
    
    if employes_sans_compte > 0:
        alertes.append(f"{employes_sans_compte} employé(s) sans compte d'accès au système")
    
    # Bulletins non validés
    bulletins_non_valides = bulletins_mois.filter(valide=False).count()
    if bulletins_non_valides > 0:
        alertes.append(f"{bulletins_non_valides} bulletin(s) en attente de validation")
    
    # Employés récemment ajoutés (7 derniers jours)
    employes_recents = Employe.objects.filter(
        date_creation__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # Contexte pour le template
    context = {
        'user_role': 'admin',
        'total_employes': total_employes,
        'employes_inactifs': employes_inactifs,
        'employes_recents': employes_recents,
        'employes_avec_compte': employes_avec_compte,
        'employes_sans_compte': employes_sans_compte,
        'masse_salariale': masse_salariale,
        'total_cotisations': total_cotisations_somme,
        'absences_attente': absences_attente,
        'bulletins_non_valides': bulletins_non_valides,
        'alertes': alertes,
        'mois_actuel': mois_actuel,
        'annee_actuelle': annee_actuelle,
    }
    
    return render(request, 'paie/dashboard_admin.html', context)  # Already modern


@login_required
def dashboard_rh(request):
    """Dashboard pour les responsables RH - Redirection vers SPA moderne"""
    return redirect('paie:accueil_moderne')
    elements_mois = ElementPaie.objects.filter(
        mois_application=mois_actuel,
        annee_application=annee_actuelle
    )
    
    # Prochaines échéances
    echeances = []
    jour_actuel = timezone.now().day
    
    if jour_actuel < 25:
        echeances.append("25: Calcul des bulletins de paie")
    if jour_actuel < 30:
        echeances.append("30: Envoi des bulletins aux employés")
    if jour_actuel < 5 or jour_actuel > 25:  # Début du mois suivant
        echeances.append("05: Déclaration CNSS du mois précédent")
    
    # Employés prioritaires (avec éléments de paie à traiter)
    employes_prioritaires = []
    for element in elements_mois.select_related('employe')[:5]:
        employes_prioritaires.append({
            'employe': element.employe,
            'action': f"{element.get_type_element_display()} à traiter"
        })
    
    context = {
        'user_role': 'rh',
        'total_employes': total_employes,
        'bulletins_calcules': bulletins_calcules,
        'bulletins_restants': total_employes - bulletins_calcules,
        'absences_attente': nb_absences_attente,
        'echeances': echeances,
        'employes_prioritaires': employes_prioritaires,
        'mois_actuel': mois_actuel,
        'annee_actuelle': annee_actuelle,
    }
    
    return render(request, 'paie/dashboard_rh.html', context)  # Already modern


@login_required
def dashboard_employe(request):
    """Dashboard pour les employés - Redirection vers SPA moderne"""
    return redirect('paie:accueil_moderne')
    
    # Solde de congés (simulation - à calculer vraiment plus tard)
    from django.db.models import Sum
    conges_pris = Absence.objects.filter(
        employe=employe,
        type_absence='CONGE',
        statut='APPROUVE',
        date_debut__year=timezone.now().year
    ).aggregate(total=Sum('nombre_jours'))['total'] or 0
    
    solde_conges = max(0, 22 - conges_pris)  # 22 congés payés annuels
    solde_rtt = 5      # RTT disponibles (à améliorer)
    
    # Dernières absences
    absences_recentes = Absence.objects.filter(employe=employe)[:3]
    
    context = {
        'user_role': 'employe',
        'employe': employe,
        'dernier_bulletin': dernier_bulletin,
        'solde_conges': solde_conges,
        'solde_rtt': solde_rtt,
        'absences_recentes': absences_recentes,
    }
    
    return render(request, 'paie/dashboard_employe.html', context)  # Already modern


# REMPLACER la fonction liste_employes dans paie/views.py par :

@login_required
def liste_employes(request):
    """Affiche la liste de tous les employés avec filtres hiérarchiques Site → Département"""
    
    # Récupérer les paramètres de filtrage
    site_filtre = request.GET.get('site', '')
    departement_filtre = request.GET.get('departement', '')
    recherche = request.GET.get('recherche', '')
    
    # Base query : employés actifs avec relations
    employes = Employe.objects.filter(actif=True).select_related('site', 'departement', 'manager')
    
    # Appliquer les filtres
    if site_filtre:
        employes = employes.filter(site_id=site_filtre)
    
    if departement_filtre:
        employes = employes.filter(departement_id=departement_filtre)
    
    if recherche:
        employes = employes.filter(
            models.Q(nom__icontains=recherche) |
            models.Q(prenom__icontains=recherche) |
            models.Q(matricule__icontains=recherche) |
            models.Q(fonction__icontains=recherche)
        )
    
    # Ordonner par hiérarchie
    employes = employes.order_by('site__nom', 'departement__nom', 'matricule')
    
    # Statistiques globales
    total_employes = employes.count()
    
    # Statistiques par site
    sites_stats = []
    for site in Site.objects.filter(actif=True).order_by('nom'):
        employes_site = employes.filter(site=site)
        if employes_site.exists():
            sites_stats.append({
                'site': site,
                'nombre_employes': employes_site.count(),
                'masse_salariale': sum(emp.salaire_base for emp in employes_site),
                'departements': employes_site.values('departement__nom').distinct().count()
            })
    
    # Calculs simples
    if employes:
        masse_salariale_totale = sum(emp.salaire_base for emp in employes)
        salaire_moyen = masse_salariale_totale / total_employes
    else:
        masse_salariale_totale = 0
        salaire_moyen = 0
    
    # Données pour les filtres
    sites_disponibles = Site.objects.filter(actif=True).order_by('nom')
    departements_disponibles = Departement.objects.filter(actif=True).order_by('site__nom', 'nom')
    
    # Si un site est sélectionné, filtrer les départements
    if site_filtre:
        departements_disponibles = departements_disponibles.filter(site_id=site_filtre)
    
    # Déterminer le rôle de l'utilisateur
    role = obtenir_role_utilisateur(request.user)
    
    context = {
        'employes': employes,
        'total_employes': total_employes,
        'masse_salariale_totale': masse_salariale_totale,
        'salaire_moyen': salaire_moyen,
        'sites_stats': sites_stats,
        'sites_disponibles': sites_disponibles,
        'departements_disponibles': departements_disponibles,
        'site_filtre': site_filtre,
        'departement_filtre': departement_filtre,
        'recherche': recherche,
        'user_role': role,
    }
    
    return render(request, 'paie/liste_employes_moderne.html', context)
def detail_employe(request, employe_id):
    """Affiche les détails d'un employé"""
    
    employe = get_object_or_404(Employe, id=employe_id)
    
    # Vérifier les permissions
    role = obtenir_role_utilisateur(request.user)
    if role == 'employe':
        # Un employé ne peut voir que ses propres infos
        gestionnaire = GestionnaireUtilisateurs()
        employe_connecte = gestionnaire.obtenir_employe_par_user(request.user)
        if not employe_connecte or employe_connecte.id != employe.id:
            return redirect('paie:dashboard_employe')
    
    # Derniers bulletins de paie
    bulletins = BulletinPaie.objects.filter(employe=employe)[:6]
    
    # Dernières absences
    absences = Absence.objects.filter(employe=employe)[:5]
    
    # Éléments de paie récents
    elements = ElementPaie.objects.filter(employe=employe)[:5]
    
    context = {
        'employe': employe,
        'bulletins': bulletins,
        'absences': absences,
        'elements': elements,
        'user_role': role,
    }
    
    return render(request, 'paie/detail_employe_moderne.html', context)


@login_required  
@audit_action('CALCULATE', 'Calcul paie mensuel - {mois}/{annee}')
def calcul_paie(request):
    """Page de calcul de la paie mensuelle - Accès Admin/RH seulement"""
    

    
    from .calculs import CalculateurPaie
    
    role = obtenir_role_utilisateur(request.user)
    context = {
        'mois_actuel': timezone.now().month,
        'annee_actuelle': timezone.now().year,
        'employes': Employe.objects.filter(actif=True),
        'message': None,
        'bulletins': [],
        'statistiques': None,
        'erreurs': [],
        'user_role': role,
    }
    
    if request.method == 'POST':
        mois = int(request.POST.get('mois'))
        annee = int(request.POST.get('annee'))
        employes_ids = request.POST.getlist('employes')  # Liste des IDs d'employés sélectionnés
        action = request.POST.get('action', 'calculer')
        
        # Si aucun employé sélectionné, prendre tous les employés actifs
        if not employes_ids:
            employes_a_traiter = Employe.objects.filter(actif=True)
        else:
            employes_a_traiter = Employe.objects.filter(id__in=employes_ids, actif=True)
        
        calculateur = CalculateurPaie()
        
        if action == 'calculer':
            # Calcul massif de la paie
            resultats = calculateur.calculer_paie_massive(
                employes_a_traiter, 
                mois, 
                annee, 
                request.user
            )
            
            context.update({
                'message': f'Calcul terminé ! {resultats["total_reussi"]} bulletins générés sur {resultats["total_traite"]} employés.',
                'bulletins': resultats['bulletins_crees'],
                'erreurs': resultats['erreurs'],
                'mois_traite': mois,
                'annee_traitee': annee,
                'statistiques': {
                    'total_employes': resultats['total_traite'],
                    'bulletins_generes': resultats['total_reussi'],
                    'erreurs_count': resultats['total_erreurs'],
                    'masse_salariale_brute': sum(b.salaire_brut_imposable for b in resultats['bulletins_crees']),
                    'total_cotisations': sum(b.cotisation_cnss + b.cotisation_amo + b.cotisation_cimr for b in resultats['bulletins_crees']),
                    'total_ir': sum(b.impot_revenu for b in resultats['bulletins_crees']),
                    'masse_salariale_nette': sum(b.net_a_payer for b in resultats['bulletins_crees'])
                }
            })
            log_calculation(
                user=request.user,
                calculation_type='PAIE_MENSUELLE', 
                details=f'Calcul paie {mois}/{annee} - {resultats["total_reussi"]} employés traités',
                request=request
            )
        elif action == 'preview':
            # Aperçu du calcul pour un employé
            employe_id = request.POST.get('employe_preview')
            if employe_id:
                employe = Employe.objects.get(id=employe_id)
                bulletin_data = calculateur.calculer_bulletin_complet(employe, mois, annee)
                context.update({
                    'preview_bulletin': bulletin_data,
                    'mois_traite': mois,
                    'annee_traitee': annee
                })
    
    # Récupérer les bulletins existants pour le mois/année actuel
    bulletins_existants = BulletinPaie.objects.filter(
        mois=context['mois_actuel'],
        annee=context['annee_actuelle']
    ).select_related('employe')
    
    context['bulletins_existants'] = bulletins_existants
    
    return render(request, 'paie/calcul_paie_moderne.html', context)


@login_required
def generer_bulletin_pdf(request, bulletin_id):
    """Génère un bulletin de paie en PDF avec debug"""
    
    # Récupérer le bulletin
    bulletin = get_object_or_404(BulletinPaie, id=bulletin_id)
    
    # Vérifier les permissions
    role = obtenir_role_utilisateur(request.user)
    if role == 'employe':
        # Un employé ne peut voir que ses propres bulletins
        gestionnaire = GestionnaireUtilisateurs()
        employe_connecte = gestionnaire.obtenir_employe_par_user(request.user)
        if not employe_connecte or employe_connecte.id != bulletin.employe.id:
            return HttpResponse("Accès non autorisé", status=403)
    
    try:
        # Test 1: Vérifier ReportLab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        # Test 2: Importer notre générateur
        from .pdf_generator import BulletinPDFGenerator
        
        # Test 3: Créer le générateur
        generator = BulletinPDFGenerator()
        
        # Test 4: Générer le PDF
        response = generator.reponse_http_pdf(bulletin)
        
        if response:
            return response
        else:
            # Debug: afficher pourquoi ça n'a pas marché
            return HttpResponse(f"""
                <h1>Debug PDF pour {bulletin.employe.nom_complet()}</h1>
                <p><strong>ReportLab importé:</strong> ✅ OK</p>
                <p><strong>Générateur créé:</strong> ✅ OK</p>
                <p><strong>Problème:</strong> response est None</p>
                <p><strong>Bulletin ID:</strong> {bulletin.id}</p>
                <p><strong>Employé:</strong> {bulletin.employe.nom_complet()}</p>
                <p><strong>Période:</strong> {bulletin.periode_formatted()}</p>
                <p><a href="/calcul-paie/">Retour</a></p>
            """)
            
    except ImportError as e:
        return HttpResponse(f"""
            <h1>Erreur d'import</h1>
            <p><strong>Erreur:</strong> {str(e)}</p>
            <p><a href="/calcul-paie/">Retour</a></p>
        """)
    except Exception as e:
        return HttpResponse(f"""
            <h1>Erreur générale</h1>
            <p><strong>Erreur:</strong> {str(e)}</p>
            <p><strong>Type:</strong> {type(e).__name__}</p>
            <p><a href="/calcul-paie/">Retour</a></p>
        """)


# =====================================
# GESTION DES ABSENCES - NOUVELLES FONCTIONS
# =====================================

@login_required
@audit_action('CREATE', 'Demande absence - {type_absence}', target_model='Absence')
def gestion_absences(request):
    """Page de gestion des absences avec permissions par rôle"""
    
    role = obtenir_role_utilisateur(request.user)
    gestionnaire = GestionnaireUtilisateurs()
    employe_actuel = gestionnaire.obtenir_employe_par_user(request.user)
    
    # Statistiques générales pour RH/Admin
    if role in ['admin', 'rh']:
        absences_en_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
        absences_du_mois = Absence.objects.filter(
            date_debut__month=timezone.now().month,
            date_debut__year=timezone.now().year
        ).count()
        
        # Demandes en attente pour validation
        demandes_attente = Absence.objects.filter(statut='EN_ATTENTE').select_related('employe').order_by('-date_creation')[:10]
        
        role_utilisateur = 'rh'
    else:
        absences_en_attente = 0
        absences_du_mois = 0
        demandes_attente = []
        role_utilisateur = 'employe'
    
    # Absences de l'employé actuel
    if employe_actuel:
        mes_absences = Absence.objects.filter(employe=employe_actuel).order_by('-date_creation')[:5]
        
        # Calcul des soldes de congés (simulation)
        from django.db.models import Sum
        conges_pris = Absence.objects.filter(
            employe=employe_actuel,
            type_absence='CONGE',
            statut='APPROUVE',
            date_debut__year=timezone.now().year
        ).aggregate(total=Sum('nombre_jours'))['total'] or 0
        
        solde_conges_restant = max(0, 22 - conges_pris)  # 22 jours de congés payés
        solde_rtt = 5      # RTT disponibles
    else:
        mes_absences = []
        solde_conges_restant = 0
        solde_rtt = 0
    
    context = {
        'role_utilisateur': role_utilisateur,
        'employe_actuel': employe_actuel,
        'absences_en_attente': absences_en_attente,
        'absences_du_mois': absences_du_mois,
        'demandes_attente': demandes_attente,
        'mes_absences': mes_absences,
        'solde_conges_restant': solde_conges_restant,
        'solde_rtt': solde_rtt,
        'message': None,
        'erreur': None,
        'user_role': role,
    }
    
    # Traitement du formulaire de demande
    if request.method == 'POST' and employe_actuel:
        try:
            type_absence = request.POST.get('type_absence')
            date_debut = request.POST.get('date_debut')
            date_fin = request.POST.get('date_fin')
            motif = request.POST.get('motif', '')
            
            # Validation des données
            if not all([type_absence, date_debut, date_fin]):
                context['erreur'] = "Tous les champs obligatoires doivent être remplis"
            else:
                # Conversion des dates
                from datetime import datetime
                date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
                date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
                
                # Validation des dates
                if date_debut_obj > date_fin_obj:
                    context['erreur'] = "La date de fin doit être après la date de début"
                elif date_debut_obj < timezone.now().date():
                    context['erreur'] = "La date de début ne peut pas être dans le passé"
                else:
                    # Calcul du nombre de jours (jours ouvrables)
                    delta = date_fin_obj - date_debut_obj
                    nombre_jours = delta.days + 1
                    
                    # Ajuster pour les weekends (approximation simple)
                    nombre_jours_ouvres = nombre_jours
                    
                    # Vérifier le solde disponible
                    if type_absence == 'CONGE' and nombre_jours_ouvres > solde_conges_restant:
                        context['erreur'] = f"Solde insuffisant. Vous avez {solde_conges_restant} jours disponibles"
                    else:
                        # Créer la demande d'absence
                        absence = Absence.objects.create(
                            employe=employe_actuel,
                            type_absence=type_absence,
                            date_debut=date_debut_obj,
                            date_fin=date_fin_obj,
                            nombre_jours=nombre_jours_ouvres,
                            motif=motif,
                            statut='EN_ATTENTE',
                            impact_salaire=(type_absence in ['SANS_SOLDE'])
                        )
                        
                        context['message'] = f"Demande d'absence créée avec succès ! ({nombre_jours_ouvres} jours)"
                        log_data_change(
                            user=request.user,
                            model_name='Absence',
                            object_id=absence.id,
                            change_type='CREATE',
                            description=f'Demande {absence.get_type_absence_display()} - {absence.nombre_jours} jours',
                            request=request
                        )
                        # Rafraîchir les données
                        context['mes_absences'] = Absence.objects.filter(employe=employe_actuel).order_by('-date_creation')[:5]
                        if type_absence == 'CONGE':
                            context['solde_conges_restant'] = solde_conges_restant - nombre_jours_ouvres
        except Exception as e:
            context['erreur'] = f"Erreur lors de la création de la demande : {str(e)}"
    
    return render(request, 'paie/gestion_absences_moderne.html', context)  # Already modern

@login_required
@audit_action('UPDATE', 'Validation absence {absence_id}', target_model='Absence')  
def valider_absence(request, absence_id):
    """Valider ou refuser une demande d'absence (RH/Admin seulement)"""
    
    # Vérifier que l'utilisateur est RH ou Admin
    role = obtenir_role_utilisateur(request.user)
    if role not in ['admin', 'rh']:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    absence = get_object_or_404(Absence, id=absence_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        note_rh = request.POST.get('note_rh', '')
        
        # Vérifier que la demande est encore en attente
        if absence.statut != 'EN_ATTENTE':
            return JsonResponse({
                'error': f'Cette demande a déjà été {absence.get_statut_display().lower()}'
            }, status=400)
        
        if action == 'approuver':
            # Vérifications supplémentaires pour l'approbation
            
            # 1. Vérifier les conflits avec d'autres absences
            conflits = Absence.objects.filter(
                employe=absence.employe,
                statut='APPROUVE',
                date_debut__lte=absence.date_fin,
                date_fin__gte=absence.date_debut
            ).exclude(id=absence.id)
            
            if conflits.exists():
                return JsonResponse({
                    'error': f'Conflit détecté avec une autre absence approuvée du {conflits.first().date_debut} au {conflits.first().date_fin}'
                }, status=400)
            
            # 2. Vérifier le solde de congés si nécessaire
            if absence.type_absence == 'CONGE':
                conges_pris = Absence.objects.filter(
                    employe=absence.employe,
                    type_absence='CONGE',
                    statut='APPROUVE',
                    date_debut__year=absence.date_debut.year
                ).aggregate(total=Sum('nombre_jours'))['total'] or 0
                
                if conges_pris + absence.nombre_jours > 22:  # 22 jours de congés payés
                    return JsonResponse({
                        'error': f'Solde insuffisant. L\'employé a déjà pris {conges_pris} jours cette année.'
                    }, status=400)
            
            absence.statut = 'APPROUVE'
            message = f"Demande d'absence de {absence.employe.nom_complet()} approuvée avec succès"
            
        elif action == 'refuser':
            absence.statut = 'REFUSE'
            message = f"Demande d'absence de {absence.employe.nom_complet()} refusée"
            
        else:
            return JsonResponse({'error': 'Action non reconnue'}, status=400)
        
        # Sauvegarder les modifications
        absence.approuve_par = request.user
        absence.date_approbation = timezone.now()
        absence.note_rh = note_rh
        absence.save()
        
        # Retourner une réponse JSON pour AJAX
        return JsonResponse({
            'success': True,
            'message': message,
            'nouveau_statut': absence.get_statut_display(),
            'absence_id': absence.id
        })
    
    # Si c'est une requête GET, retourner les détails de l'absence
    return JsonResponse({
        'absence': {
            'id': absence.id,
            'employe': absence.employe.nom_complet(),
            'matricule': absence.employe.matricule,
            'type': absence.get_type_absence_display(),
            'date_debut': absence.date_debut.strftime('%d/%m/%Y'),
            'date_fin': absence.date_fin.strftime('%d/%m/%Y'),
            'nombre_jours': absence.nombre_jours,
            'motif': absence.motif or 'Aucun motif spécifié',
            'date_demande': absence.date_creation.strftime('%d/%m/%Y à %H:%M')
        }
    })


@login_required
def validation_lot_absences(request):
    """Validation en lot des absences (RH/Admin seulement)"""
    
    role = obtenir_role_utilisateur(request.user)
    if role not in ['admin', 'rh']:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    if request.method == 'POST':
        absences_ids = request.POST.getlist('absences_ids')
        action = request.POST.get('action')
        note_rh = request.POST.get('note_rh', '')
        
        if not absences_ids:
            return JsonResponse({'error': 'Aucune absence sélectionnée'}, status=400)
        
        absences = Absence.objects.filter(
            id__in=absences_ids,
            statut='EN_ATTENTE'
        )
        
        if not absences.exists():
            return JsonResponse({'error': 'Aucune absence en attente trouvée'}, status=400)
        
        resultats = []
        erreurs = []
        
        for absence in absences:
            try:
                if action == 'approuver':
                    # Vérifications similaires à la validation individuelle
                    conflits = Absence.objects.filter(
                        employe=absence.employe,
                        statut='APPROUVE',
                        date_debut__lte=absence.date_fin,
                        date_fin__gte=absence.date_debut
                    ).exclude(id=absence.id)
                    
                    if conflits.exists():
                        erreurs.append(f"{absence.employe.nom_complet()}: Conflit avec autre absence")
                        continue
                    
                    absence.statut = 'APPROUVE'
                elif action == 'refuser':
                    absence.statut = 'REFUSE'
                
                absence.approuve_par = request.user
                absence.date_approbation = timezone.now()
                absence.note_rh = note_rh
                absence.save()
                
                resultats.append(absence.employe.nom_complet())
                
            except Exception as e:
                erreurs.append(f"{absence.employe.nom_complet()}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'message': f"{len(resultats)} absence(s) {action}ée(s) avec succès",
            'resultats': resultats,
            'erreurs': erreurs
        })
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@login_required
def statistiques_absences(request):
    """Statistiques détaillées des absences pour RH/Admin"""
    
    role = obtenir_role_utilisateur(request.user)
    if role not in ['admin', 'rh']:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    # Statistiques du mois en cours
    mois_actuel = timezone.now().month
    annee_actuelle = timezone.now().year
    
    stats = {
        'mois_actuel': {
            'total_demandes': Absence.objects.filter(
                date_creation__month=mois_actuel,
                date_creation__year=annee_actuelle
            ).count(),
            'en_attente': Absence.objects.filter(
                statut='EN_ATTENTE'
            ).count(),
            'approuvees': Absence.objects.filter(
                statut='APPROUVE',
                date_debut__month=mois_actuel,
                date_debut__year=annee_actuelle
            ).count(),
            'refusees': Absence.objects.filter(
                statut='REFUSE',
                date_creation__month=mois_actuel,
                date_creation__year=annee_actuelle
            ).count(),
        },
        'par_type': [],
        'employes_les_plus_absents': []
    }
    
    # Statistiques par type d'absence
    from django.db.models import Count
    types_absences = Absence.objects.filter(
        date_debut__year=annee_actuelle
    ).values('type_absence').annotate(
        count=Count('id')
    ).order_by('-count')
    
    for type_abs in types_absences:
        stats['par_type'].append({
            'type': dict(Absence.TYPE_ABSENCE_CHOICES)[type_abs['type_absence']],
            'count': type_abs['count']
        })
    
    # Employés avec le plus d'absences cette année
    employes_absences = Absence.objects.filter(
        date_debut__year=annee_actuelle,
        statut='APPROUVE'
    ).values(
        'employe__nom', 'employe__prenom', 'employe__matricule'
    ).annotate(
        total_jours=Sum('nombre_jours'),
        total_absences=Count('id')
    ).order_by('-total_jours')[:5]
    
    for emp in employes_absences:
        stats['employes_les_plus_absents'].append({
            'nom_complet': f"{emp['employe__nom']} {emp['employe__prenom']}",
            'matricule': emp['employe__matricule'],
            'total_jours': emp['total_jours'],
            'total_absences': emp['total_absences']
        })
    
    return render(request, 'paie/statistiques_absences_moderne.html', {'stats': stats, 'user_role': role})


@login_required
def calendrier_absences(request):
    """Calendrier des absences pour la vue d'ensemble"""
    
    role = obtenir_role_utilisateur(request.user)
    if role not in ['admin', 'rh']:
        return redirect('paie:dashboard_employe')
    
    # Récupérer toutes les absences approuvées du mois
    absences_mois = Absence.objects.filter(
        statut='APPROUVE',
        date_debut__month=timezone.now().month,
        date_debut__year=timezone.now().year
    ).select_related('employe').order_by('date_debut')
    
    context = {
        'absences_mois': absences_mois,
        'mois_actuel': timezone.now().strftime('%B %Y'),
        'user_role': role,
    }
    
    return render(request, 'paie/calendrier_absences_moderne.html', context)


@login_required
def test_calcul_absences(request):
    """
    Vue de test pour vérifier l'intégration des absences dans la paie
    """
    role = obtenir_role_utilisateur(request.user)
    if role not in ['admin', 'rh']:
        return redirect('paie:dashboard_employe')
    
    from .calculs import CalculateurPaie
    from django.utils import timezone
    
    context = {
        'tests_effectues': [],
        'erreurs': [],
        'employes': Employe.objects.filter(actif=True),
        'user_role': role,
    }
    
    if request.method == 'POST':
        employe_id = request.POST.get('employe_id')
        mois = int(request.POST.get('mois', timezone.now().month))
        annee = int(request.POST.get('annee', timezone.now().year))
        
        if employe_id:
            try:
                employe = Employe.objects.get(id=employe_id)
                calculateur = CalculateurPaie()
                
                # Test 1: Calcul des absences seul
                absences_info = calculateur.calculer_absences(employe, mois, annee)
                
                # Test 2: Calcul du bulletin complet
                bulletin_data = calculateur.calculer_bulletin_complet(employe, mois, annee)
                
                # Test 3: Récupérer les absences de l'employé pour ce mois
                absences_du_mois = Absence.objects.filter(
                    employe=employe,
                    statut='APPROUVE',
                    date_debut__month__lte=mois,
                    date_fin__month__gte=mois,
                    date_debut__year__lte=annee,
                    date_fin__year__gte=annee
                )
                
                test_result = {
                    'employe': employe,
                    'mois': mois,
                    'annee': annee,
                    'salaire_base': employe.salaire_base,
                    'absences_trouvees': absences_du_mois,
                    'absences_info': absences_info,
                    'bulletin_data': bulletin_data,
                    'impact_calcule': absences_info['deduction_montant'] > 0
                }
                
                context['tests_effectues'].append(test_result)
                
            except Exception as e:
                context['erreurs'].append({
                    'employe_id': employe_id,
                    'erreur': str(e)
                })
    
    return render(request, 'paie/test_calcul_absences_moderne.html', context)


@login_required
def deconnexion_vue(request):
    """Vue personnalisée de déconnexion"""
    logout(request)
    return redirect('paie:accueil')  
# Ajoutez cette fonction à la fin de votre fichier paie/views.py

@login_required
def page_aide(request):
    """Page d'aide avec tous les liens et guides de navigation"""
    
    context = {
        'user_role': obtenir_role_utilisateur(request.user),
    }
    
    return render(request, 'paie/aide_moderne.html', context)
@staff_member_required
def gestion_rubriques_employe(request, employe_id):
    """
    Interface pour gérer toutes les rubriques d'un employé spécifique
    Permet d'ajouter/modifier/supprimer n'importe quel montant
    """
    employe = get_object_or_404(Employe, id=employe_id)
    
    # Récupérer toutes les assignations actives
    assignations = EmployeRubrique.objects.filter(
        employe=employe,
        actif=True
    ).select_related('rubrique').order_by('rubrique__type_rubrique', 'rubrique__nom')
    
    # Récupérer toutes les rubriques disponibles
    rubriques_disponibles = RubriquePersonnalisee.objects.filter(
        actif=True
    ).order_by('type_rubrique', 'nom')
    
    # Calculer le total des rubriques pour cet employé
    total_gains = sum(
        a.calculer_montant(date.today().month, date.today().year, employe.salaire_base, employe.salaire_base)
        for a in assignations if a.rubrique.type_rubrique == 'GAIN'
    )
    total_retenues = sum(
        a.calculer_montant(date.today().month, date.today().year, employe.salaire_base, employe.salaire_base)
        for a in assignations if a.rubrique.type_rubrique == 'RETENUE'
    )
    total_allocations = sum(
        a.calculer_montant(date.today().month, date.today().year, employe.salaire_base, employe.salaire_base)
        for a in assignations if a.rubrique.type_rubrique == 'ALLOCATION'
    )
    
    context = {
        'employe': employe,
        'assignations': assignations,
        'rubriques_disponibles': rubriques_disponibles,
        'total_gains': total_gains,
        'total_retenues': total_retenues,
        'total_allocations': total_allocations,
        'nouveau_salaire_brut': employe.salaire_base + total_gains + total_allocations,
        'nouveau_net_estimé': employe.salaire_base + total_gains + total_allocations - total_retenues
    }
    
    return render(request, 'paie/gestion_rubriques_employe_moderne.html', context)

@staff_member_required
def ajouter_rubrique_ponctuelle(request):
    """
    Ajouter une rubrique ponctuelle (montant libre) à un employé
    AJAX endpoint pour ajouts rapides
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            employe_id = data.get('employe_id')
            nom_rubrique = data.get('nom_rubrique')
            type_rubrique = data.get('type_rubrique', 'GAIN')
            montant = Decimal(str(data.get('montant', 0)))
            commentaire = data.get('commentaire', '')
            mois = data.get('mois', date.today().month)
            annee = data.get('annee', date.today().year)
            
            employe = get_object_or_404(Employe, id=employe_id)
            
            # Créer une rubrique ponctuelle
            code_rubrique = f"PONCT_{employe.matricule}_{date.today().strftime('%Y%m%d_%H%M%S')}"
            
            with transaction.atomic():
                # Créer la rubrique
                rubrique = RubriquePersonnalisee.objects.create(
                    code=code_rubrique,
                    nom=nom_rubrique,
                    description=f"Rubrique ponctuelle pour {employe.nom_complet()}",
                    type_rubrique=type_rubrique,
                    mode_calcul='FIXE',
                    montant_fixe=montant,
                    periodicite='PONCTUEL',
                    soumis_ir=(type_rubrique in ['GAIN']),
                    soumis_cnss=(type_rubrique in ['GAIN']),
                    soumis_amo=(type_rubrique in ['GAIN']),
                    date_debut=date(annee, mois, 1),
                    date_fin=date(annee, mois, 28),  # Valide que pour ce mois
                    cree_par=request.user
                )
                
                # Assigner à l'employé
                assignation = EmployeRubrique.objects.create(
                    employe=employe,
                    rubrique=rubrique,
                    date_debut=date(annee, mois, 1),
                    date_fin=date(annee, mois, 28),
                    actif=True,
                    commentaire=commentaire,
                    cree_par=request.user
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Rubrique "{nom_rubrique}" ajoutée avec succès',
                'assignation_id': assignation.id,
                'montant': float(montant)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

@staff_member_required
def modifier_assignation_rubrique(request, assignation_id):
    """
    Modifier une assignation existante (montant personnalisé, dates, etc.)
    """
    assignation = get_object_or_404(EmployeRubrique, id=assignation_id)
    
    if request.method == 'POST':
        try:
            # Récupérer les nouvelles valeurs
            nouveau_montant = request.POST.get('montant_personnalise')
            nouveau_pourcentage = request.POST.get('pourcentage_personnalise')
            date_debut = request.POST.get('date_debut')
            date_fin = request.POST.get('date_fin')
            commentaire = request.POST.get('commentaire', '')
            actif = request.POST.get('actif') == 'on'
            
            # Mettre à jour l'assignation
            if nouveau_montant:
                assignation.montant_personnalise = Decimal(nouveau_montant)
                assignation.pourcentage_personnalise = None
            elif nouveau_pourcentage:
                assignation.pourcentage_personnalise = Decimal(nouveau_pourcentage)
                assignation.montant_personnalise = None
            
            if date_debut:
                assignation.date_debut = date_debut
            if date_fin:
                assignation.date_fin = date_fin
            
            assignation.commentaire = commentaire
            assignation.actif = actif
            assignation.save()
            
            messages.success(request, f'Assignation "{assignation.rubrique.nom}" mise à jour')
            
        except Exception as e:
            messages.error(request, f'Erreur: {e}')
    
    return redirect('gestion_rubriques_employe', employe_id=assignation.employe.id)

@staff_member_required
def supprimer_assignation_rubrique(request, assignation_id):
    """
    Supprimer une assignation de rubrique
    """
    assignation = get_object_or_404(EmployeRubrique, id=assignation_id)
    employe_id = assignation.employe.id
    nom_rubrique = assignation.rubrique.nom
    
    if request.method == 'POST':
        assignation.actif = False  # Désactiver plutôt que supprimer pour historique
        assignation.save()
        messages.success(request, f'Rubrique "{nom_rubrique}" supprimée')
    
    return redirect('gestion_rubriques_employe', employe_id=employe_id)

@staff_member_required
def assignation_massive_rubriques(request):
    """
    Interface pour assigner une rubrique à plusieurs employés à la fois
    """
    if request.method == 'POST':
        try:
            employes_ids = request.POST.getlist('employes')
            rubrique_id = request.POST.get('rubrique')
            montant_personnalise = request.POST.get('montant_personnalise')
            date_debut = request.POST.get('date_debut')
            date_fin = request.POST.get('date_fin', '')
            commentaire = request.POST.get('commentaire', '')
            
            rubrique = get_object_or_404(RubriquePersonnalisee, id=rubrique_id)
            employes = Employe.objects.filter(id__in=employes_ids, actif=True)
            
            assignations_creees = 0
            with transaction.atomic():
                for employe in employes:
                    # Vérifier si l'assignation existe déjà
                    if not EmployeRubrique.objects.filter(
                        employe=employe, 
                        rubrique=rubrique, 
                        actif=True
                    ).exists():
                        assignation = EmployeRubrique.objects.create(
                            employe=employe,
                            rubrique=rubrique,
                            montant_personnalise=Decimal(montant_personnalise) if montant_personnalise else None,
                            date_debut=date_debut,
                            date_fin=date_fin if date_fin else None,
                            commentaire=commentaire,
                            actif=True,
                            cree_par=request.user
                        )
                        assignations_creees += 1
            
            messages.success(
                request, 
                f'Rubrique "{rubrique.nom}" assignée à {assignations_creees} employé(s)'
            )
            
        except Exception as e:
            messages.error(request, f'Erreur lors de l\'assignation massive: {e}')
    
    # Récupérer les données pour le formulaire
    employes = Employe.objects.filter(actif=True).order_by('nom', 'prenom')
    rubriques = RubriquePersonnalisee.objects.filter(actif=True).order_by('type_rubrique', 'nom')
    
    context = {
        'employes': employes,
        'rubriques': rubriques
    }
    
    return render(request, 'paie/assignation_massive_moderne.html', context)

@staff_member_required
def dashboard_rubriques_admin(request):
    """
    Dashboard complet pour l'admin : vue d'ensemble de toutes les rubriques
    """
    # Statistiques générales
    total_rubriques = RubriquePersonnalisee.objects.filter(actif=True).count()
    total_assignations = EmployeRubrique.objects.filter(actif=True).count()
    
    # Rubriques les plus utilisées
    rubriques_populaires = RubriquePersonnalisee.objects.filter(
        actif=True
    ).annotate(
        nb_assignations=models.Count('employes_assignes', filter=models.Q(employes_assignes__actif=True))
    ).order_by('-nb_assignations')[:10]
    
    # Employés avec le plus de rubriques
    employes_rubriques = Employe.objects.filter(
        actif=True
    ).annotate(
        nb_rubriques=models.Count('rubriques_personnalisees', filter=models.Q(rubriques_personnalisees__actif=True))
    ).order_by('-nb_rubriques')[:10]
    
    # Rubriques récentes
    rubriques_recentes = RubriquePersonnalisee.objects.filter(
        actif=True
    ).order_by('-date_creation')[:10]
    
    # Calcul des montants totaux par type
    from django.db.models import Sum, Case, When, DecimalField
    
    totaux_par_type = EmployeRubrique.objects.filter(
        actif=True,
        rubrique__actif=True
    ).values('rubrique__type_rubrique').annotate(
        total_fixe=Sum(
            Case(
                When(rubrique__mode_calcul='FIXE', then='rubrique__montant_fixe'),
                default=0,
                output_field=DecimalField()
            )
        ),
        nb_assignations=Count('id')
    )
    
    context = {
        'total_rubriques': total_rubriques,
        'total_assignations': total_assignations,
        'rubriques_populaires': rubriques_populaires,
        'employes_rubriques': employes_rubriques,
        'rubriques_recentes': rubriques_recentes,
        'totaux_par_type': totaux_par_type
    }
    
    return render(request, 'paie/dashboard_rubriques_admin_moderne.html', context)
@staff_member_required
def gestion_rubriques_employe(request, employe_id):
    """Interface simple pour gérer les rubriques d'un employé"""
    employe = get_object_or_404(Employe, id=employe_id)
    
    # Récupérer les assignations
    assignations = EmployeRubrique.objects.filter(
        employe=employe,
        actif=True
    ).select_related('rubrique')
    
    # Calculer les totaux
    total_gains = sum(
        a.montant_personnalise or a.rubrique.montant_fixe 
        for a in assignations 
        if a.rubrique.type_rubrique == 'GAIN'
    )
    
    total_retenues = sum(
        a.montant_personnalise or a.rubrique.montant_fixe 
        for a in assignations 
        if a.rubrique.type_rubrique == 'RETENUE'
    )
    
    total_allocations = sum(
        a.montant_personnalise or a.rubrique.montant_fixe 
        for a in assignations 
        if a.rubrique.type_rubrique == 'ALLOCATION'
    )
    
    # Template simple en HTML intégré
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gestion Rubriques - {employe.nom_complet()}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h2>Gestion des Rubriques - {employe.nom_complet()}</h2>
            
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card text-white bg-primary">
                        <div class="card-body">
                            <h5>Employé</h5>
                            <p>Matricule: {employe.matricule}<br>
                            Salaire: {employe.salaire_base} DH</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-white bg-success">
                        <div class="card-body">
                            <h5>Gains</h5>
                            <h3>{total_gains} DH</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-white bg-danger">
                        <div class="card-body">
                            <h5>Retenues</h5>
                            <h3>{total_retenues} DH</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-white bg-info">
                        <div class="card-body">
                            <h5>Allocations</h5>
                            <h3>{total_allocations} DH</h3>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h5>Rubriques Actives ({assignations.count()})</h5>
                </div>
                <div class="card-body">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Rubrique</th>
                                <th>Type</th>
                                <th>Montant</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for assignation in assignations:
        montant = assignation.montant_personnalise or assignation.rubrique.montant_fixe
        type_badge = {
            'GAIN': 'success',
            'RETENUE': 'danger', 
            'ALLOCATION': 'info',
            'COTISATION': 'warning'
        }.get(assignation.rubrique.type_rubrique, 'secondary')
        
        html_content += f"""
                            <tr>
                                <td><strong>{assignation.rubrique.nom}</strong><br>
                                    <small>{assignation.rubrique.code}</small></td>
                                <td><span class="badge bg-{type_badge}">{assignation.rubrique.type_rubrique}</span></td>
                                <td><strong>{montant} DH</strong></td>
                                <td>
                                    <a href="/admin/paie/employerubrique/{assignation.id}/change/" 
                                       class="btn btn-sm btn-primary">Modifier</a>
                                </td>
                            </tr>
        """
    
    html_content += f"""
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="mt-4">
                <a href="/admin/paie/employerubrique/add/?employe={employe.id}" 
                   class="btn btn-success">Ajouter Nouvelle Rubrique</a>
                <a href="/admin/paie/employe/{employe.id}/change/" 
                   class="btn btn-secondary">Retour à l'Employé</a>
            </div>
            
            <div class="mt-4">
                <h4>Nouveau Salaire Estimé</h4>
                <p class="lead">
                    Salaire base: {employe.salaire_base} DH<br>
                    + Gains: {total_gains} DH<br>
                    + Allocations: {total_allocations} DH<br>
                    - Retenues: {total_retenues} DH<br>
                    <strong>= Total estimé: {employe.salaire_base + total_gains + total_allocations - total_retenues} DH</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_content)

@staff_member_required
def assignation_massive_rubriques(request):
    """Interface simple pour assignation massive"""
    if request.method == 'POST':
        messages.success(request, "Fonctionnalité en cours de développement")
        return redirect('/admin/paie/employerubrique/')
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Assignation Massive</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h2>Assignation Massive de Rubriques</h2>
            <div class="alert alert-info">
                <h4>Fonctionnalité Simplifiée</h4>
                <p>Pour l'instant, utilisez l'admin Django pour les assignations:</p>
                <a href="/admin/paie/employerubrique/add/" class="btn btn-primary">
                    Ajouter une Assignation
                </a>
                <a href="/admin/paie/employerubrique/" class="btn btn-secondary">
                    Voir toutes les Assignations
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

@staff_member_required
def dashboard_rubriques_admin(request):
    """Dashboard simple des rubriques"""
    total_rubriques = RubriquePersonnalisee.objects.filter(actif=True).count()
    total_assignations = EmployeRubrique.objects.filter(actif=True).count()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Rubriques</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h2>Dashboard des Rubriques Personnalisées</h2>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5>Statistiques</h5>
                            <p>Rubriques actives: <strong>{total_rubriques}</strong></p>
                            <p>Assignations actives: <strong>{total_assignations}</strong></p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5>Actions Rapides</h5>
                            <a href="/admin/paie/rubriquepersonnalisee/" class="btn btn-primary">
                                Gérer les Rubriques
                            </a><br><br>
                            <a href="/admin/paie/employerubrique/" class="btn btn-success">
                                Gérer les Assignations
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)

# Vues pour les autres fonctionnalités (stubs pour éviter les erreurs)
@staff_member_required  
def ajouter_rubrique_ponctuelle(request):
    return JsonResponse({'success': False, 'error': 'Fonctionnalité en développement'})

@staff_member_required
def modifier_assignation_rubrique(request, assignation_id):
    return redirect('/admin/paie/employerubrique/')

@staff_member_required
def supprimer_assignation_rubrique(request, assignation_id):
    return redirect('/admin/paie/employerubrique/')

# Vues modernes manquantes

@login_required
def dashboard_admin_moderne(request):
    """Dashboard moderne pour les administrateurs - Redirection vers SPA"""
    return redirect('paie:accueil_moderne')

@login_required 
def dashboard_rh_moderne(request):
    """Dashboard moderne pour les RH - Redirection vers SPA"""
    return redirect('paie:accueil_moderne')

@login_required
def aide(request):
    """Page d'aide du système"""
    context = {
        'titre': 'Aide & Documentation',
        'utilisateur_connecte': request.user,
        'role_utilisateur': obtenir_role_utilisateur(request.user),
    }
    return render(request, 'paie/aide_moderne.html', context)

# Vues API pour la gestion des absences

@login_required
def api_approve_absence(request, absence_id):
    """API pour approuver une absence"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Vérification des permissions
        role = obtenir_role_utilisateur(request.user)
        if role not in ['admin', 'rh']:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'}, status=403)
        
        absence = get_object_or_404(Absence, id=absence_id)
        absence.statut = 'APPROUVE'
        absence.save()
        
        # Log de l'action
        audit_action(
            request.user,
            'MODIFICATION',
            f"Absence approuvée pour {absence.employe.nom} {absence.employe.prenom}",
            {'absence_id': absence_id, 'nouveau_statut': 'APPROUVE'}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Absence approuvée avec succès',
            'new_status': 'APPROUVE'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_reject_absence(request, absence_id):
    """API pour rejeter une absence"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Vérification des permissions
        role = obtenir_role_utilisateur(request.user)
        if role not in ['admin', 'rh']:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'}, status=403)
        
        absence = get_object_or_404(Absence, id=absence_id)
        absence.statut = 'REFUSE'
        absence.save()
        
        # Log de l'action
        audit_action(
            request.user,
            'MODIFICATION',
            f"Absence refusée pour {absence.employe.nom} {absence.employe.prenom}",
            {'absence_id': absence_id, 'nouveau_statut': 'REFUSE'}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Absence refusée',
            'new_status': 'REFUSE'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@login_required
def accueil_moderne_fixed(request):
    """Page d'accueil SPA moderne - Version corrigée"""
    
    try:
        # Statistiques pour le dashboard
        total_employes = Employe.objects.filter(actif=True).count()
        
        # Absences en attente
        absences_attente = 0
        try:
            from .models import Absence
            absences_attente = Absence.objects.filter(statut='EN_ATTENTE').count()
        except:
            pass
        
        # Calcul de la masse salariale
        employes_actifs = Employe.objects.filter(actif=True)
        masse_salariale = sum(employe.salaire_base for employe in employes_actifs)
        
        # Nouveaux employés du mois
        from datetime import datetime
        debut_mois = datetime.now().replace(day=1)
        nouveaux_employes = Employe.objects.filter(
            date_embauche__gte=debut_mois,
            actif=True
        ).count()
        
        context = {
            'total_employes': total_employes,
            'absences_attente': absences_attente,
            'masse_salariale': masse_salariale,
            'nouveaux_employes': nouveaux_employes,
        }
        
        return render(request, 'paie/accueil_moderne_fixed.html', context)
        
    except Exception as e:
        # En cas d'erreur, rediriger vers une page simple
        messages.error(request, f'Erreur lors du chargement du dashboard: {str(e)}')
        return redirect('admin:index')


# ===== API VIEWS POUR LES FONCTIONNALITÉS SPA =====

@login_required
@require_http_methods(["POST"])
def api_calculate_payroll(request, employe_id):
    """API pour calculer la paie d'un employé"""
    try:
        employe = Employe.objects.get(id=employe_id, actif=True)
        
        # Logique de calcul de paie simplifiée
        salaire_base = employe.salaire_base or 0
        
        # Simulation d'un calcul de paie
        # Ici vous pouvez implémenter la vraie logique de calcul
        cotisations_sociales = salaire_base * 0.15  # 15% de cotisations
        impot_sur_revenu = max(0, (salaire_base - 2500) * 0.10)  # Impôt simplifié
        
        salaire_net = salaire_base - cotisations_sociales - impot_sur_revenu
        
        # Créer ou mettre à jour le bulletin de paie
        bulletin, created = BulletinPaie.objects.get_or_create(
            employe=employe,
            mois=datetime.now().month,
            annee=datetime.now().year,
            defaults={
                'salaire_base': salaire_base,
                'salaire_net': salaire_net,
                'cotisations': cotisations_sociales,
                'impots': impot_sur_revenu,
                'date_calcul': datetime.now().date()
            }
        )
        
        if not created:
            # Mettre à jour si existant
            bulletin.salaire_base = salaire_base
            bulletin.salaire_net = salaire_net
            bulletin.cotisations = cotisations_sociales
            bulletin.impots = impot_sur_revenu
            bulletin.date_calcul = datetime.now().date()
            bulletin.save()
        
        return JsonResponse({
            'success': True,
            'montant': salaire_net,
            'employe': f"{employe.prenom} {employe.nom}",
            'details': {
                'salaire_base': salaire_base,
                'cotisations': cotisations_sociales,
                'impots': impot_sur_revenu,
                'salaire_net': salaire_net
            }
        })
        
    except Employe.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Employé non trouvé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du calcul: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_calculate_all_payroll(request):
    """API pour calculer la paie de tous les employés actifs"""
    try:
        employes = Employe.objects.filter(actif=True)
        employes_traites = 0
        erreurs = []
        
        for employe in employes:
            try:
                # Réutiliser la logique de calcul individuel
                salaire_base = employe.salaire_base or 0
                cotisations_sociales = salaire_base * 0.15
                impot_sur_revenu = max(0, (salaire_base - 2500) * 0.10)
                salaire_net = salaire_base - cotisations_sociales - impot_sur_revenu
                
                bulletin, created = BulletinPaie.objects.get_or_create(
                    employe=employe,
                    mois=datetime.now().month,
                    annee=datetime.now().year,
                    defaults={
                        'salaire_base': salaire_base,
                        'salaire_net': salaire_net,
                        'cotisations': cotisations_sociales,
                        'impots': impot_sur_revenu,
                        'date_calcul': datetime.now().date()
                    }
                )
                
                if not created:
                    bulletin.salaire_base = salaire_base
                    bulletin.salaire_net = salaire_net
                    bulletin.cotisations = cotisations_sociales
                    bulletin.impots = impot_sur_revenu
                    bulletin.date_calcul = datetime.now().date()
                    bulletin.save()
                
                employes_traites += 1
                
            except Exception as e:
                erreurs.append(f"Erreur pour {employe.nom}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'employes_traites': employes_traites,
            'total_employes': employes.count(),
            'erreurs': erreurs,
            'message': f'Calcul terminé: {employes_traites} employés traités'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du calcul global: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_export_payroll(request):
    """API pour exporter les données de paie"""
    try:
        # Pour l'instant, retourner un message de développement
        # Ici vous pouvez implémenter l'export réel (Excel, PDF, etc.)
        
        return JsonResponse({
            'success': False,
            'error': 'Fonctionnalité d\'export en développement',
            'message': 'L\'export des données de paie sera disponible prochainement'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'export: {str(e)}'
        }, status=500)


# ===== NOUVELLES FONCTIONS API COMPLÈTES =====

@login_required
def api_calculate_payroll_complete(request, employe_id):
    """API COMPLÈTE pour calculer la paie d'un employé spécifique"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Vérification des permissions
        role = obtenir_role_utilisateur(request.user)
        if role not in ['admin', 'rh']:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'}, status=403)
        
        employe = get_object_or_404(Employe, id=employe_id)
        
        # Import du calculateur de paie si disponible
        try:
            from .calculs import CalculateurPaie
            calculateur = CalculateurPaie()
            mois = timezone.now().month
            annee = timezone.now().year
            
            # Calculer la paie avec le système existant
            resultats = calculateur.calculer_bulletin_complet(employe, mois, annee)
            
            if resultats.get('success', False):
                # Créer le bulletin de paie
                bulletin = BulletinPaie.objects.create(
                    employe=employe,
                    mois=mois,
                    annee=annee,
                    salaire_brut=resultats.get('salaire_brut', 0),
                    salaire_net=resultats.get('salaire_net', 0),
                    cotisations_totales=resultats.get('cotisations_totales', 0),
                    calcule_par=request.user,
                    date_calcul=timezone.now()
                )
                
                # Log de l'action
                log_calculation(
                    user=request.user,
                    description=f"Paie calculée pour {employe.nom} {employe.prenom} - {mois}/{annee}",
                    details={'employe_id': employe_id, 'bulletin_id': bulletin.id, 'montant': float(resultats.get('salaire_net', 0))},
                    request=request
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'Paie calculée pour {employe.nom} {employe.prenom}',
                    'employe': f'{employe.nom} {employe.prenom}',
                    'montant': float(resultats.get('salaire_net', 0)),
                    'salaire_brut': float(resultats.get('salaire_brut', 0)),
                    'bulletin_id': bulletin.id,
                    'details': resultats
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': resultats.get('error', 'Erreur lors du calcul')
                })
                
        except ImportError:
            # Calcul simple si le module calculs n'existe pas
            salaire_brut = employe.salaire_base or 0
            cotisations = salaire_brut * Decimal('0.2')  # 20% de cotisations
            salaire_net = salaire_brut - cotisations
            
            # Créer un bulletin simple
            bulletin = BulletinPaie.objects.create(
                employe=employe,
                mois=timezone.now().month,
                annee=timezone.now().year,
                salaire_brut=salaire_brut,
                salaire_net=salaire_net,
                cotisations_totales=cotisations,
                calcule_par=request.user,
                date_calcul=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Paie calculée pour {employe.nom} {employe.prenom}',
                'employe': f'{employe.nom} {employe.prenom}',
                'montant': float(salaire_net),
                'salaire_brut': float(salaire_brut),
                'bulletin_id': bulletin.id
            })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False, 
            'error': f'Erreur système: {str(e)}',
            'debug': traceback.format_exc()
        }, status=500)


@login_required
def api_calculate_all_payroll_complete(request):
    """API COMPLÈTE pour calculer la paie de tous les employés actifs"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Vérification des permissions
        role = obtenir_role_utilisateur(request.user)
        if role not in ['admin', 'rh']:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'}, status=403)
        
        # Récupérer tous les employés actifs
        employes = Employe.objects.filter(actif=True)
        employes_traites = 0
        employes_reussis = 0
        erreurs = []
        bulletins_crees = []
        
        for employe in employes:
            try:
                # Calculer la paie pour chaque employé
                salaire_brut = employe.salaire_base or 0
                cotisations = salaire_brut * Decimal('0.2')  # 20% de cotisations
                salaire_net = salaire_brut - cotisations
                
                # Créer ou mettre à jour le bulletin
                bulletin, created = BulletinPaie.objects.get_or_create(
                    employe=employe,
                    mois=timezone.now().month,
                    annee=timezone.now().year,
                    defaults={
                        'salaire_brut': salaire_brut,
                        'salaire_net': salaire_net,
                        'cotisations_totales': cotisations,
                        'calcule_par': request.user,
                        'date_calcul': timezone.now()
                    }
                )
                
                if not created:
                    # Mettre à jour le bulletin existant
                    bulletin.salaire_brut = salaire_brut
                    bulletin.salaire_net = salaire_net
                    bulletin.cotisations_totales = cotisations
                    bulletin.calcule_par = request.user
                    bulletin.date_calcul = timezone.now()
                    bulletin.save()
                
                bulletins_crees.append({
                    'employe': f'{employe.nom} {employe.prenom}',
                    'montant': float(salaire_net),
                    'bulletin_id': bulletin.id
                })
                
                employes_traites += 1
                employes_reussis += 1
                
            except Exception as e:
                erreurs.append(f"Erreur pour {employe.nom} {employe.prenom}: {str(e)}")
                employes_traites += 1
        
        # Log de l'action globale
        log_calculation(
            user=request.user,
            description=f"Calcul massif de paie - {timezone.now().month}/{timezone.now().year}",
            details={
                'total_employes': employes.count(),
                'traites': employes_traites,
                'reussis': employes_reussis,
                'echecs': len(erreurs)
            },
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'message': f"Calcul terminé: {employes_reussis} sur {employes_traites} employés traités avec succès",
            'employes_traites': employes_traites,
            'employes_reussis': employes_reussis,
            'employes_echecs': len(erreurs),
            'bulletins_crees': bulletins_crees,
            'erreurs': erreurs
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False, 
            'error': f'Erreur système: {str(e)}',
            'debug': traceback.format_exc()
        }, status=500)


@login_required
def api_export_payroll_complete(request):
    """API COMPLÈTE pour exporter les bulletins de paie"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Vérification des permissions
        role = obtenir_role_utilisateur(request.user)
        if role not in ['admin', 'rh']:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'}, status=403)
        
        mois = request.GET.get('mois', timezone.now().month)
        annee = request.GET.get('annee', timezone.now().year)
        
        # Récupérer les bulletins du mois
        bulletins = BulletinPaie.objects.filter(
            mois=mois,
            annee=annee
        ).select_related('employe').order_by('employe__nom')
        
        if not bulletins.exists():
            return JsonResponse({
                'success': False,
                'error': f'Aucun bulletin trouvé pour {mois}/{annee}'
            })
        
        # Créer les données d'export
        export_data = []
        total_brut = 0
        total_net = 0
        
        for bulletin in bulletins:
            data = {
                'employe': f'{bulletin.employe.nom} {bulletin.employe.prenom}',
                'matricule': bulletin.employe.matricule or 'N/A',
                'salaire_brut': float(bulletin.salaire_brut or 0),
                'salaire_net': float(bulletin.salaire_net or 0),
                'cotisations': float(bulletin.cotisations_totales or 0),
                'date_calcul': bulletin.date_calcul.strftime('%d/%m/%Y %H:%M') if bulletin.date_calcul else 'N/A',
                'mois': bulletin.mois,
                'annee': bulletin.annee
            }
            export_data.append(data)
            total_brut += data['salaire_brut']
            total_net += data['salaire_net']
        
        return JsonResponse({
            'success': True,
            'data': export_data,
            'total_bulletins': len(export_data),
            'periode': f'{mois}/{annee}',
            'totaux': {
                'total_brut': total_brut,
                'total_net': total_net,
                'total_cotisations': total_brut - total_net
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ===== API GESTION ABSENCES =====

@login_required
def api_approve_absence(request, absence_id):
    """API pour approuver une demande d'absence"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Vérification des permissions
        role = obtenir_role_utilisateur(request.user)
        if role not in ['admin', 'rh']:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'}, status=403)
        
        absence = get_object_or_404(Absence, id=absence_id)
        
        if absence.statut != 'EN_ATTENTE':
            return JsonResponse({
                'success': False,
                'error': f'Cette absence a déjà été traitée (statut: {absence.get_statut_display()})'
            })
        
        # Approuver l'absence
        absence.statut = 'APPROUVEE'
        absence.validee_par = request.user
        absence.date_validation = timezone.now()
        absence.save()
        
        # Log de l'action
        log_data_change(
            user=request.user,
            model_name='Absence',
            object_id=absence.id,
            change_type='UPDATE',
            description=f'Absence approuvée - {absence.employe.nom} {absence.employe.prenom}',
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Absence de {absence.employe.nom} {absence.employe.prenom} approuvée',
            'absence_id': absence.id,
            'nouveau_statut': absence.get_statut_display()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'approbation: {str(e)}'
        }, status=500)


@login_required
def api_reject_absence(request, absence_id):
    """API pour rejeter une demande d'absence"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Vérification des permissions
        role = obtenir_role_utilisateur(request.user)
        if role not in ['admin', 'rh']:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'}, status=403)
        
        absence = get_object_or_404(Absence, id=absence_id)
        
        if absence.statut != 'EN_ATTENTE':
            return JsonResponse({
                'success': False,
                'error': f'Cette absence a déjà été traitée (statut: {absence.get_statut_display()})'
            })
        
        # Récupérer le motif du refus
        import json
        try:
            body = json.loads(request.body.decode('utf-8'))
            motif = body.get('motif', '')
        except:
            motif = request.POST.get('motif', '')
        
        # Rejeter l'absence
        absence.statut = 'REFUSEE'
        absence.validee_par = request.user
        absence.date_validation = timezone.now()
        absence.motif_refus = motif
        absence.save()
        
        # Log de l'action
        log_data_change(
            user=request.user,
            model_name='Absence',
            object_id=absence.id,
            change_type='UPDATE',
            description=f'Absence refusée - {absence.employe.nom} {absence.employe.prenom} - Motif: {motif}',
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Absence de {absence.employe.nom} {absence.employe.prenom} refusée',
            'absence_id': absence.id,
            'nouveau_statut': absence.get_statut_display(),
            'motif': motif
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du refus: {str(e)}'
        }, status=500)
