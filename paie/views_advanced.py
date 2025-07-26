# paie/views_advanced.py
"""
Vues avancées avec filtres par site et département pour gérer de grandes quantités d'employés
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Employe, Site, Departement, Absence, BulletinPaie
from .decorators import rh_required, admin_required
from .user_management import obtenir_role_utilisateur
import json


@login_required
@rh_required
def liste_employes_avancee(request):
    """
    Vue avancée pour la gestion des employés avec filtres multiples
    Optimisée pour gérer de grandes quantités d'employés
    """
    # Récupération des paramètres de filtrage
    site_filtre = request.GET.get('site', '')
    departement_filtre = request.GET.get('departement', '')
    fonction_filtre = request.GET.get('fonction', '')
    statut_filtre = request.GET.get('statut', '')
    recherche = request.GET.get('recherche', '')
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 25)

    # Query de base avec optimisations
    employes = Employe.objects.select_related(
        'site', 'departement', 'manager', 'user'
    ).prefetch_related('equipe')

    # Application des filtres
    if site_filtre:
        employes = employes.filter(site_id=site_filtre)
    
    if departement_filtre:
        employes = employes.filter(departement_id=departement_filtre)
    
    if fonction_filtre:
        employes = employes.filter(fonction__icontains=fonction_filtre)
    
    if statut_filtre == 'actif':
        employes = employes.filter(actif=True)
    elif statut_filtre == 'inactif':
        employes = employes.filter(actif=False)
    
    if recherche:
        employes = employes.filter(
            Q(nom__icontains=recherche) |
            Q(prenom__icontains=recherche) |
            Q(matricule__icontains=recherche) |
            Q(fonction__icontains=recherche) |
            Q(email__icontains=recherche)
        )

    # Tri par défaut
    employes = employes.order_by('site__nom', 'departement__nom', 'matricule')

    # Pagination
    paginator = Paginator(employes, per_page)
    employes_page = paginator.get_page(page)

    # Statistiques globales (optimisées)
    stats = {
        'total_employes': employes.count(),
        'employes_actifs': employes.filter(actif=True).count(),
        'masse_salariale': employes.aggregate(Sum('salaire_base'))['salaire_base__sum'] or 0,
        'salaire_moyen': employes.aggregate(Avg('salaire_base'))['salaire_base__avg'] or 0,
    }

    # Statistiques par site
    sites_stats = []
    sites_avec_employes = Site.objects.filter(
        employes__in=employes
    ).annotate(
        nb_employes=Count('employes'),
        masse_salariale_site=Sum('employes__salaire_base')
    ).distinct()

    for site in sites_avec_employes:
        sites_stats.append({
            'site': site,
            'nombre_employes': site.nb_employes,
            'masse_salariale': site.masse_salariale_site or 0,
            'pourcentage': round((site.nb_employes / stats['total_employes']) * 100, 1) if stats['total_employes'] > 0 else 0
        })

    # Données pour les filtres
    sites_disponibles = Site.objects.filter(actif=True).annotate(
        nb_employes=Count('employes', filter=Q(employes__actif=True))
    ).order_by('nom')

    departements_disponibles = Departement.objects.filter(actif=True).select_related('site')
    if site_filtre:
        departements_disponibles = departements_disponibles.filter(site_id=site_filtre)
    departements_disponibles = departements_disponibles.annotate(
        nb_employes=Count('employes', filter=Q(employes__actif=True))
    ).order_by('site__nom', 'nom')

    # Fonctions disponibles
    fonctions_disponibles = employes.values_list('fonction', flat=True).distinct().order_by('fonction')

    context = {
        'employes': employes_page,
        'stats': stats,
        'sites_stats': sites_stats,
        'sites_disponibles': sites_disponibles,
        'departements_disponibles': departements_disponibles,
        'fonctions_disponibles': fonctions_disponibles,
        'filtres': {
            'site': site_filtre,
            'departement': departement_filtre,
            'fonction': fonction_filtre,
            'statut': statut_filtre,
            'recherche': recherche,
        },
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
        },
        'user_role': obtenir_role_utilisateur(request.user),
    }

    # Réponse AJAX pour les filtres dynamiques
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'html': render(request, 'paie/employes_table_partial.html', context).content.decode(),
            'stats': stats,
            'pagination': context['pagination']
        })

    return render(request, 'paie/liste_employes_moderne.html', context)


@login_required
@rh_required
def gestion_utilisateurs_avancee(request):
    """
    Vue avancée pour la gestion des utilisateurs avec filtres
    """
    # Filtres
    site_filtre = request.GET.get('site', '')
    departement_filtre = request.GET.get('departement', '')
    role_filtre = request.GET.get('role', '')
    statut_filtre = request.GET.get('statut', '')
    recherche = request.GET.get('recherche', '')

    # Employés avec compte
    employes_avec_compte = Employe.objects.select_related(
        'user', 'site', 'departement'
    ).filter(user__isnull=False)

    # Employés sans compte
    employes_sans_compte = Employe.objects.filter(
        user__isnull=True, actif=True
    ).select_related('site', 'departement')

    # Application des filtres pour les deux groupes
    filtres_q = Q()
    if site_filtre:
        filtres_q &= Q(site_id=site_filtre)
    if departement_filtre:
        filtres_q &= Q(departement_id=departement_filtre)
    if recherche:
        filtres_q &= (
            Q(nom__icontains=recherche) |
            Q(prenom__icontains=recherche) |
            Q(email__icontains=recherche) |
            Q(matricule__icontains=recherche)
        )

    employes_avec_compte = employes_avec_compte.filter(filtres_q)
    employes_sans_compte = employes_sans_compte.filter(filtres_q)

    # Filtres spécifiques aux utilisateurs
    if role_filtre:
        employes_avec_compte = employes_avec_compte.filter(role_systeme=role_filtre)
    
    if statut_filtre == 'actif':
        employes_avec_compte = employes_avec_compte.filter(user__is_active=True, actif=True)
    elif statut_filtre == 'inactif':
        employes_avec_compte = employes_avec_compte.filter(
            Q(user__is_active=False) | Q(actif=False)
        )

    # Statistiques
    stats = {
        'employes_total': Employe.objects.filter(actif=True).count(),
        'avec_compte': employes_avec_compte.count(),
        'sans_compte': employes_sans_compte.count(),
        'comptes_rh': employes_avec_compte.filter(role_systeme='RH').count(),
        'comptes_employes': employes_avec_compte.filter(role_systeme='EMPLOYE').count(),
        'jamais_connectes': employes_avec_compte.filter(user__last_login__isnull=True).count(),
    }

    # Données pour les filtres
    sites_disponibles = Site.objects.filter(actif=True).order_by('nom')
    departements_disponibles = Departement.objects.filter(actif=True).select_related('site')
    if site_filtre:
        departements_disponibles = departements_disponibles.filter(site_id=site_filtre)

    context = {
        'employes_avec_compte': employes_avec_compte,
        'employes_sans_compte': employes_sans_compte,
        'stats': stats,
        'sites_disponibles': sites_disponibles,
        'departements_disponibles': departements_disponibles,
        'filtres': {
            'site': site_filtre,
            'departement': departement_filtre,
            'role': role_filtre,
            'statut': statut_filtre,
            'recherche': recherche,
        },
        'user_role': obtenir_role_utilisateur(request.user),
    }

    return render(request, 'paie/gestion_utilisateurs_moderne.html', context)


@login_required
@rh_required
def calcul_paie_avance(request):
    """
    Vue avancée pour le calcul de paie avec filtres
    """
    # Paramètres de calcul
    mois = int(request.GET.get('mois', timezone.now().month))
    annee = int(request.GET.get('annee', timezone.now().year))
    
    # Filtres
    site_filtre = request.GET.get('site', '')
    departement_filtre = request.GET.get('departement', '')
    employe_recherche = request.GET.get('employe_recherche', '')

    # Query des employés selon les filtres
    employes = Employe.objects.select_related('site', 'departement').filter(actif=True)
    
    if site_filtre:
        employes = employes.filter(site_id=site_filtre)
    
    if departement_filtre:
        employes = employes.filter(departement_id=departement_filtre)
    
    if employe_recherche:
        employes = employes.filter(
            Q(nom__icontains=employe_recherche) |
            Q(prenom__icontains=employe_recherche) |
            Q(matricule__icontains=employe_recherche)
        )

    # Bulletins existants pour la période
    bulletins_existants = BulletinPaie.objects.filter(
        mois=mois, 
        annee=annee,
        employe__in=employes
    ).select_related('employe')

    # Statistiques de calcul
    stats_calcul = {
        'employes_total': employes.count(),
        'bulletins_calcules': bulletins_existants.count(),
        'en_attente': employes.count() - bulletins_existants.count(),
        'erreurs': 0,  # À implémenter selon votre logique
        'masse_salariale_brute': bulletins_existants.aggregate(
            Sum('salaire_brut_imposable')
        )['salaire_brut_imposable__sum'] or 0,
        'total_net': bulletins_existants.aggregate(
            Sum('net_a_payer')
        )['net_a_payer__sum'] or 0,
    }

    # Paramètres système
    parametres_systeme = {
        'taux_cnss': 4.48,
        'taux_amo': 2.26,
        'taux_cimr': 6.00,
        'frais_professionnels': 20.00,
        'plafond_cnss': 6000.00,
    }

    # Données pour les filtres
    sites_disponibles = Site.objects.filter(actif=True).annotate(
        nb_employes=Count('employes', filter=Q(employes__actif=True))
    ).order_by('nom')

    departements_disponibles = Departement.objects.filter(actif=True).select_related('site')
    if site_filtre:
        departements_disponibles = departements_disponibles.filter(site_id=site_filtre)
    departements_disponibles = departements_disponibles.annotate(
        nb_employes=Count('employes', filter=Q(employes__actif=True))
    ).order_by('site__nom', 'nom')

    context = {
        'employes': employes,
        'bulletins_existants': bulletins_existants,
        'stats_calcul': stats_calcul,
        'parametres_systeme': parametres_systeme,
        'sites_disponibles': sites_disponibles,
        'departements_disponibles': departements_disponibles,
        'periode': {
            'mois': mois,
            'annee': annee,
            'mois_nom': [
                '', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
            ][mois]
        },
        'filtres': {
            'site': site_filtre,
            'departement': departement_filtre,
            'employe_recherche': employe_recherche,
        },
        'user_role': obtenir_role_utilisateur(request.user),
    }

    return render(request, 'paie/calcul_paie_moderne.html', context)


@login_required
@rh_required
def gestion_absences_avancee(request):
    """
    Vue avancée pour la gestion des absences avec filtres
    """
    # Filtres
    site_filtre = request.GET.get('site', '')
    departement_filtre = request.GET.get('departement', '')
    type_filtre = request.GET.get('type', '')
    statut_filtre = request.GET.get('statut', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    recherche = request.GET.get('recherche', '')

    # Query de base
    absences = Absence.objects.select_related(
        'employe', 'employe__site', 'employe__departement'
    ).order_by('-date_creation')

    # Application des filtres
    if site_filtre:
        absences = absences.filter(employe__site_id=site_filtre)
    
    if departement_filtre:
        absences = absences.filter(employe__departement_id=departement_filtre)
    
    if type_filtre:
        absences = absences.filter(type_absence=type_filtre)
    
    if statut_filtre:
        absences = absences.filter(statut=statut_filtre)
    
    if date_debut:
        absences = absences.filter(date_debut__gte=date_debut)
    
    if date_fin:
        absences = absences.filter(date_fin__lte=date_fin)
    
    if recherche:
        absences = absences.filter(
            Q(employe__nom__icontains=recherche) |
            Q(employe__prenom__icontains=recherche) |
            Q(motif__icontains=recherche)
        )

    # Statistiques des absences
    today = timezone.now().date()
    debut_mois = today.replace(day=1)
    
    stats_absences = {
        'demandes_attente': absences.filter(statut='EN_ATTENTE').count(),
        'absences_mois': absences.filter(
            date_debut__gte=debut_mois,
            date_debut__lt=debut_mois.replace(month=debut_mois.month + 1) if debut_mois.month < 12 
            else debut_mois.replace(year=debut_mois.year + 1, month=1)
        ).count(),
        'conges_approuves': absences.filter(
            statut='APPROUVE',
            type_absence='CONGE'
        ).count(),
        'absences_sans_solde': absences.filter(
            statut='APPROUVE',
            type_absence='SANS_SOLDE'
        ).count(),
    }

    # Pagination
    paginator = Paginator(absences, 20)
    page = request.GET.get('page', 1)
    absences_page = paginator.get_page(page)

    # Données pour les filtres
    sites_disponibles = Site.objects.filter(actif=True).order_by('nom')
    departements_disponibles = Departement.objects.filter(actif=True).select_related('site')
    if site_filtre:
        departements_disponibles = departements_disponibles.filter(site_id=site_filtre)

    context = {
        'absences': absences_page,
        'stats_absences': stats_absences,
        'sites_disponibles': sites_disponibles,
        'departements_disponibles': departements_disponibles,
        'types_absences': Absence.TYPE_CHOICES,
        'statuts_absences': Absence.STATUT_CHOICES,
        'filtres': {
            'site': site_filtre,
            'departement': departement_filtre,
            'type': type_filtre,
            'statut': statut_filtre,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'recherche': recherche,
        },
        'user_role': obtenir_role_utilisateur(request.user),
    }

    return render(request, 'paie/gestion_absences_moderne.html', context)


@login_required
def api_departements_par_site(request, site_id):
    """
    API pour récupérer les départements d'un site (AJAX)
    """
    departements = Departement.objects.filter(
        site_id=site_id, 
        actif=True
    ).values('id', 'nom', 'code').order_by('nom')
    
    return JsonResponse(list(departements), safe=False)


@login_required
def api_statistiques_site(request, site_id):
    """
    API pour récupérer les statistiques d'un site (AJAX)
    """
    site = get_object_or_404(Site, id=site_id)
    employes_site = Employe.objects.filter(site=site, actif=True)
    
    stats = {
        'nombre_employes': employes_site.count(),
        'masse_salariale': employes_site.aggregate(Sum('salaire_base'))['salaire_base__sum'] or 0,
        'salaire_moyen': employes_site.aggregate(Avg('salaire_base'))['salaire_base__avg'] or 0,
        'departements': employes_site.values('departement__nom').annotate(
            count=Count('id')
        ).order_by('departement__nom')
    }
    
    return JsonResponse(stats)


@login_required
@rh_required
def export_employes_excel_avance(request):
    """
    Export Excel avancé avec filtres
    """
    # Récupérer les mêmes filtres que la vue liste
    site_filtre = request.GET.get('site', '')
    departement_filtre = request.GET.get('departement', '')
    fonction_filtre = request.GET.get('fonction', '')
    statut_filtre = request.GET.get('statut', '')
    recherche = request.GET.get('recherche', '')

    # Appliquer les filtres (même logique que liste_employes_avancee)
    employes = Employe.objects.select_related('site', 'departement', 'manager')
    
    if site_filtre:
        employes = employes.filter(site_id=site_filtre)
    if departement_filtre:
        employes = employes.filter(departement_id=departement_filtre)
    if fonction_filtre:
        employes = employes.filter(fonction__icontains=fonction_filtre)
    if statut_filtre == 'actif':
        employes = employes.filter(actif=True)
    elif statut_filtre == 'inactif':
        employes = employes.filter(actif=False)
    if recherche:
        employes = employes.filter(
            Q(nom__icontains=recherche) |
            Q(prenom__icontains=recherche) |
            Q(matricule__icontains=recherche)
        )

    # Utiliser votre système d'export existant
    try:
        from .excel_export import ExporteurExcelPayrollPro
        exporteur = ExporteurExcelPayrollPro()
        
        excel_file = exporteur.export_employes_avec_filtres(
            employes, 
            filtres={
                'site': site_filtre,
                'departement': departement_filtre,
                'fonction': fonction_filtre,
                'statut': statut_filtre,
                'recherche': recherche,
            }
        )
        
        if excel_file:
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="employes_filtrés_{timezone.now().strftime("%Y%m%d_%H%M")}.xlsx"'
            excel_file.seek(0)
            response.write(excel_file.read())
            return response
        else:
            return JsonResponse({'error': 'Erreur lors de la génération'}, status=500)
            
    except ImportError:
        return JsonResponse({'error': 'Module d\'export non disponible'}, status=500)


# Fonctions utilitaires pour les templates
def get_sites_with_stats():
    """Récupère les sites avec leurs statistiques"""
    return Site.objects.filter(actif=True).annotate(
        nb_employes=Count('employes', filter=Q(employes__actif=True)),
        masse_salariale=Sum('employes__salaire_base', filter=Q(employes__actif=True))
    ).order_by('nom')


def get_departements_with_stats(site_id=None):
    """Récupère les départements avec leurs statistiques"""
    departements = Departement.objects.filter(actif=True).select_related('site')
    
    if site_id:
        departements = departements.filter(site_id=site_id)
    
    return departements.annotate(
        nb_employes=Count('employes', filter=Q(employes__actif=True))
    ).order_by('site__nom', 'nom')