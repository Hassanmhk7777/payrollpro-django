# Imports Django
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
# Imports locaux
from .models import Employe, ParametrePaie, ElementPaie, Absence, BulletinPaie
from .user_management import GestionnaireUtilisateurs, obtenir_role_utilisateur
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .decorators import admin_required, rh_required, employe_required, safe_user_access
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
    
    return render(request, 'paie/accueil.html', context)

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
    
    return render(request, 'paie/connexion_simple.html')
@login_required
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
    return render(request, 'paie/creer_comptes.html', context)
@login_required
def dashboard_admin(request):
    """Dashboard pour les administrateurs"""

    
    # Statistiques générales
    total_employes = Employe.objects.filter(actif=True).count()
    employes_inactifs = Employe.objects.filter(actif=False).count()
    
    # Statistiques de paie du mois en cours
    mois_actuel = timezone.now().month
    annee_actuelle = timezone.now().year
    
    # Bulletins du mois
    bulletins_mois = BulletinPaie.objects.filter(
        mois=mois_actuel, 
        annee=annee_actuelle
    )
    
    # Calculs financiers
    masse_salariale = bulletins_mois.aggregate(Sum('salaire_brut_imposable'))['salaire_brut_imposable__sum'] or 0
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
    
    return render(request, 'paie/dashboard_admin.html', context)


@login_required
def dashboard_rh(request):
    """Dashboard pour les responsables RH"""
    

    
    # Tâches du jour
    mois_actuel = timezone.now().month
    annee_actuelle = timezone.now().year
    
    # Employés actifs
    employes_actifs = Employe.objects.filter(actif=True)
    total_employes = employes_actifs.count()
    
    # Bulletins de paie du mois
    bulletins_mois = BulletinPaie.objects.filter(mois=mois_actuel, annee=annee_actuelle)
    bulletins_calcules = bulletins_mois.count()
    
    # Absences à valider
    absences_attente = Absence.objects.filter(statut='EN_ATTENTE')
    nb_absences_attente = absences_attente.count()
    
    # Employés avec éléments de paie à traiter
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
    
    return render(request, 'paie/dashboard_rh.html', context)


@login_required
def dashboard_employe(request):
    """Dashboard pour les employés"""
    
    # Récupérer l'employé lié à l'utilisateur
    gestionnaire = GestionnaireUtilisateurs()
    employe = gestionnaire.obtenir_employe_par_user(request.user)
    
    if not employe:
        # Si l'utilisateur n'est pas lié à un employé, rediriger vers admin
        if request.user.is_superuser:
            return redirect('paie:dashboard_admin')
        else:
            # Cas d'erreur - utilisateur sans employé associé
            return render(request, 'paie/erreur_acces.html', {
                'message': "Votre compte n'est pas associé à un employé. Contactez votre administrateur."
            })
    
    # Dernier bulletin de paie
    dernier_bulletin = BulletinPaie.objects.filter(employe=employe).first()
    
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
    
    return render(request, 'paie/dashboard_employe.html', context)


@login_required
def liste_employes(request):
    """Affiche la liste de tous les employés - Accès restreint Admin/RH"""
    

    
    # Récupérer tous les employés actifs
    employes = Employe.objects.filter(actif=True).order_by('matricule')
    
    # Statistiques rapides
    total_employes = employes.count()
    
    # Calculs simples
    if employes:
        masse_salariale_totale = sum(emp.salaire_base for emp in employes)
        salaire_moyen = masse_salariale_totale / total_employes
    else:
        masse_salariale_totale = 0
        salaire_moyen = 0
    
    # Déterminer le rôle de l'utilisateur
    role = obtenir_role_utilisateur(request.user)
    context = {
        'employes': employes,
        'total_employes': total_employes,
        'masse_salariale_totale': masse_salariale_totale,
        'salaire_moyen': salaire_moyen,
        'user_role': role,
    }
    
    return render(request, 'paie/liste_employes_simple.html', context)


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
    
    return render(request, 'paie/detail_employe.html', context)


@login_required
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
    
    return render(request, 'paie/calcul_paie.html', context)


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
                        
                        # Rafraîchir les données
                        context['mes_absences'] = Absence.objects.filter(employe=employe_actuel).order_by('-date_creation')[:5]
                        if type_absence == 'CONGE':
                            context['solde_conges_restant'] = solde_conges_restant - nombre_jours_ouvres
                        
        except Exception as e:
            context['erreur'] = f"Erreur lors de la création de la demande : {str(e)}"
    
    return render(request, 'paie/gestion_absences.html', context)


@login_required
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
    
    return JsonResponse(stats)


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
    
    return render(request, 'paie/calendrier_absences.html', context)


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
    
    return render(request, 'paie/test_calcul_absences.html', context)


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
    
    return render(request, 'paie/aide.html', context)