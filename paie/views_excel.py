# paie/views_excel.py
"""
Vues pour l'export Excel intégrées à votre système existant
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from .models import Employe, BulletinPaie
from .decorators import rh_required, admin_required, role_required
from .excel_export import ExporteurExcelPayrollPro
from .user_management import obtenir_role_utilisateur
from .excel_cnss import ExporteurCNSS
from django.db.models import Count, Sum

@login_required
@rh_required
def export_bulletin_excel(request, bulletin_id):
    """
    Export d'un bulletin individuel en Excel
    Compatible avec votre vue PDF existante
    """
    bulletin = get_object_or_404(BulletinPaie, id=bulletin_id)
    
    # Vérifier les permissions (même logique que votre PDF)
    role = obtenir_role_utilisateur(request.user)
    if role == 'employe':
        from .user_management import GestionnaireUtilisateurs
        gestionnaire = GestionnaireUtilisateurs()
        employe_connecte = gestionnaire.obtenir_employe_par_user(request.user)
        if not employe_connecte or employe_connecte.id != bulletin.employe.id:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    try:
        exporteur = ExporteurExcelPayrollPro()
        excel_file = exporteur.export_bulletin_individuel(bulletin)
        
        if excel_file:
            filename = f"bulletin_{bulletin.employe.matricule}_{bulletin.mois:02d}_{bulletin.annee}.xlsx"
            return exporteur.reponse_http_excel(excel_file, filename)
        else:
            return JsonResponse({
                'error': 'Erreur lors de la génération du fichier Excel'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'error': f'Erreur: {str(e)}'
        }, status=500)


@login_required
@rh_required
def export_bulletins_massif_excel(request):
    """
    Export massif des bulletins d'un mois en Excel
    Intégration avec votre page de calcul de paie
    """
    if request.method == 'POST':
        mois = int(request.POST.get('mois', timezone.now().month))
        annee = int(request.POST.get('annee', timezone.now().year))
        employes_ids = request.POST.getlist('employes')  # IDs sélectionnés
        
        # Si aucun employé sélectionné, prendre tous les bulletins du mois
        if not employes_ids:
            bulletins = BulletinPaie.objects.filter(mois=mois, annee=annee)
        else:
            bulletins = BulletinPaie.objects.filter(
                mois=mois, 
                annee=annee, 
                employe_id__in=employes_ids
            )
        
        if not bulletins.exists():
            return JsonResponse({
                'error': f'Aucun bulletin trouvé pour {mois:02d}/{annee}'
            }, status=404)
        
        try:
            exporteur = ExporteurExcelPayrollPro()
            excel_file = exporteur.export_bulletins_massif(bulletins, mois, annee)
            
            if excel_file:
                filename = f"bulletins_paie_{mois:02d}_{annee}.xlsx"
                return exporteur.reponse_http_excel(excel_file, filename)
            else:
                return JsonResponse({
                    'error': 'Erreur lors de la génération du fichier Excel'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Erreur: {str(e)}'
            }, status=500)
    
    # Si GET, afficher la page de sélection
    context = {
        'mois_actuel': timezone.now().month,
        'annee_actuelle': timezone.now().year,
        'employes': Employe.objects.filter(actif=True),
        'user_role': obtenir_role_utilisateur(request.user),
    }
    
    return render(request, 'paie/export_excel.html', context)


@login_required
@rh_required  
def export_cnss_excel(request):
    """
    Export au format CNSS pour déclarations officielles
    """
    if request.method == 'POST':
        mois = int(request.POST.get('mois', timezone.now().month))
        annee = int(request.POST.get('annee', timezone.now().year))
        
        bulletins = BulletinPaie.objects.filter(mois=mois, annee=annee)
        
        if not bulletins.exists():
            return JsonResponse({
                'error': f'Aucun bulletin trouvé pour {mois:02d}/{annee}'
            }, status=404)
        
        try:
            exporteur = ExporteurExcelPayrollPro()
            excel_file = exporteur.export_format_cnss(bulletins, mois, annee)
            
            if excel_file:
                filename = f"declaration_cnss_{mois:02d}_{annee}.xlsx"
                return exporteur.reponse_http_excel(excel_file, filename)
            else:
                return JsonResponse({
                    'error': 'Erreur lors de la génération du fichier CNSS'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Erreur: {str(e)}'
            }, status=500)
    
    # Page de configuration
    context = {
        'mois_actuel': timezone.now().month,
        'annee_actuelle': timezone.now().year,
        'user_role': obtenir_role_utilisateur(request.user),
    }
    
    return render(request, 'paie/export_cnss.html', context)


@login_required
@admin_required
def statistiques_excel(request):
    """
    Export des statistiques RH en Excel
    """
    if request.method == 'POST':
        type_stats = request.POST.get('type_stats', 'mensuel')
        
        try:
            exporteur = ExporteurExcelPayrollPro()
            
            if type_stats == 'mensuel':
                excel_file = exporteur.export_statistiques_mensuelles()
            elif type_stats == 'annuel':
                excel_file = exporteur.export_statistiques_annuelles()
            else:
                return JsonResponse({'error': 'Type de statistiques non reconnu'}, status=400)
            
            if excel_file:
                filename = f"statistiques_{type_stats}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                return exporteur.reponse_http_excel(excel_file, filename)
            else:
                return JsonResponse({
                    'error': 'Erreur lors de la génération des statistiques'
                }, status=500)
                
        except Exception as e:
            return JsonResponse({
                'error': f'Erreur: {str(e)}'
            }, status=500)
    
    context = {
        'user_role': obtenir_role_utilisateur(request.user),
    }
    return render(request, 'paie/statistiques_excel.html', context) 
# REMPLACEZ la vue export_cnss_mensuel dans paie/views_excel.py par celle-ci :

@login_required
def export_cnss_mensuel(request, mois, annee):
    """
    Export CNSS mensuel au format BDS officiel
    Accessible seulement aux Admin et RH
    """
    from .user_management import obtenir_role_utilisateur
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Vérifier les permissions manuellement
    role = obtenir_role_utilisateur(request.user)
    if role not in ['admin', 'rh']:
        messages.error(request, 'Accès non autorisé à l\'export CNSS')
        return redirect('paie:accueil')
    
    try:
        # Créer l'exporteur CNSS
        from .excel_cnss import ExporteurCNSS
        exporteur = ExporteurCNSS()
        
        # Vérifier qu'il y a des bulletins pour cette période
        from .models import BulletinPaie
        bulletins_count = BulletinPaie.objects.filter(mois=mois, annee=annee).count()
        
        if bulletins_count == 0:
            messages.warning(request, 
                f"Aucun bulletin de paie trouvé pour {mois:02d}/{annee}. "
                f"Veuillez d'abord calculer la paie mensuelle.")
            return redirect('paie:calcul_paie')
        
        # Générer et retourner le fichier Excel
        response = exporteur.exporter_vers_reponse_http(mois, annee)
        
        # Log d'audit simple
        print(f"✅ Export CNSS généré: {mois:02d}/{annee} - {bulletins_count} employés - User: {request.user.username}")
        
        return response
        
    except Exception as e:
        messages.error(request, f"Erreur lors de l'export CNSS : {str(e)}")
        return redirect('paie:calcul_paie')


@login_required 
def page_export_cnss(request):
    """
    Page dédiée à l'export CNSS avec options avancées
    """
    from .models import BulletinPaie
    from django.db.models import Count, Sum
    from django.utils import timezone
    from .user_management import obtenir_role_utilisateur
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Vérifier les permissions manuellement
    role = obtenir_role_utilisateur(request.user)
    if role not in ['admin', 'rh']:
        messages.error(request, 'Accès non autorisé à l\'export CNSS')
        return redirect('paie:accueil')
    
    # Statistiques des périodes disponibles
    periodes_disponibles = BulletinPaie.objects.values('mois', 'annee').annotate(
        nb_bulletins=Count('id'),
        masse_salariale=Sum('salaire_brut_imposable')
    ).order_by('-annee', '-mois')[:12]
    
    # Paramètres CNSS actuels
    taux_cnss = {
        'cnss_salarie': 4.48,
        'amo_salarie': 2.26,
        'cnss_patronal': 20.48,
        'amo_patronal': 1.85,
        'formation_prof': 1.60
    }
    
    context = {
        'periodes_disponibles': periodes_disponibles,
        'taux_cnss': taux_cnss,
        'mois_actuel': timezone.now().month,
        'annee_actuelle': timezone.now().year,
        'user_role': role,
    }
    
    return render(request, 'paie/export_cnss.html', context)