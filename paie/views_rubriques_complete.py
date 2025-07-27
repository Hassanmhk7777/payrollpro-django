"""
Vues complètes pour la gestion des rubriques personnalisées
Correction des erreurs identifiées dans le rapport de test
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
import json
from decimal import Decimal

from .models import RubriquePersonnalisee, EmployeRubrique, Employe
from .decorators import admin_required, rh_required
from .forms import RubriqueRapideForm


@login_required
@admin_required
def rubriques_spa_view(request):
    """
    Vue SPA complète pour les rubriques avec statistiques correctes
    """
    # Toutes les rubriques actives
    rubriques = RubriquePersonnalisee.objects.filter(actif=True)
    
    # Statistiques par type
    rubriques_gains = rubriques.filter(type_rubrique='GAIN')
    rubriques_deductions = rubriques.filter(type_rubrique='RETENUE')
    rubriques_inactives = RubriquePersonnalisee.objects.filter(actif=False)
    
    # Annotate avec le nombre d'employés assignés
    rubriques = rubriques.annotate(
        nb_employes_assignes=Count('employes_assignes', filter=Q(employes_assignes__actif=True))
    ).order_by('ordre_affichage', 'nom')
    
    rubriques_gains = rubriques_gains.annotate(
        nb_employes_assignes=Count('employes_assignes', filter=Q(employes_assignes__actif=True))
    ).order_by('ordre_affichage', 'nom')
    
    rubriques_deductions = rubriques_deductions.annotate(
        nb_employes_assignes=Count('employes_assignes', filter=Q(employes_assignes__actif=True))
    ).order_by('ordre_affichage', 'nom')
    
    rubriques_inactives = rubriques_inactives.annotate(
        nb_employes_assignes=Count('employes_assignes', filter=Q(employes_assignes__actif=True))
    ).order_by('-date_modification')
    
    context = {
        'rubriques': rubriques,
        'rubriques_gains': rubriques_gains,
        'rubriques_deductions': rubriques_deductions,
        'rubriques_inactives': rubriques_inactives,
        'total_rubriques': rubriques.count(),
        'total_gains': rubriques_gains.count(),
        'total_deductions': rubriques_deductions.count(),
        'total_inactives': rubriques_inactives.count(),
    }
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'paie/spa/rubriques.html', context)
    else:
        return render(request, 'paie/base.html', {
            'section': 'rubriques',
            **context
        })


@login_required
@admin_required
@require_POST
def creer_rubrique_ajax(request):
    """
    Créer une nouvelle rubrique via AJAX
    """
    try:
        # Récupérer les données du formulaire
        code = request.POST.get('code', '').strip().upper()
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        type_rubrique = request.POST.get('type_rubrique')
        formule_calcul = request.POST.get('formule_calcul', '').strip()
        ordre = int(request.POST.get('ordre', 0))
        active = request.POST.get('active') == 'on'
        soumise_cotisations = request.POST.get('soumise_cotisations') == 'on'
        
        # Validation
        if not code or not nom or not type_rubrique:
            return JsonResponse({
                'success': False,
                'message': 'Code, nom et type sont obligatoires'
            })
        
        # Vérifier l'unicité du code
        if RubriquePersonnalisee.objects.filter(code=code).exists():
            return JsonResponse({
                'success': False,
                'message': f'Le code "{code}" existe déjà'
            })
        
        # Créer la rubrique
        rubrique = RubriquePersonnalisee.objects.create(
            code=code,
            nom=nom,
            description=description,
            type_rubrique=type_rubrique,
            formule_calcul=formule_calcul or None,
            ordre=ordre,
            actif=active,
            soumise_cotisations=soumise_cotisations,
            cree_par=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Rubrique "{nom}" créée avec succès',
            'rubrique_id': rubrique.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        })


@login_required
@admin_required
def rubrique_details_ajax(request, rubrique_id):
    """
    Récupérer les détails d'une rubrique pour édition
    """
    try:
        rubrique = get_object_or_404(RubriquePersonnalisee, id=rubrique_id)
        
        return JsonResponse({
            'success': True,
            'rubrique': {
                'id': rubrique.id,
                'code': rubrique.code,
                'nom': rubrique.nom,
                'description': rubrique.description,
                'type_rubrique': rubrique.type_rubrique,
                'formule_calcul': rubrique.formule_calcul,
                'ordre': rubrique.ordre,
                'active': rubrique.actif,
                'soumise_cotisations': rubrique.soumise_cotisations,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@login_required
@admin_required
@require_POST
def activer_rubrique_ajax(request, rubrique_id):
    """
    Réactiver une rubrique désactivée
    """
    try:
        rubrique = get_object_or_404(RubriquePersonnalisee, id=rubrique_id)
        
        if rubrique.actif:
            return JsonResponse({
                'success': False,
                'message': 'Cette rubrique est déjà active'
            })
        
        rubrique.actif = True
        rubrique.date_modification = timezone.now()
        rubrique.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Rubrique "{rubrique.nom}" réactivée avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@login_required
@admin_required
@require_POST
def supprimer_rubrique_ajax(request, rubrique_id):
    """
    Supprimer (désactiver) une rubrique
    """
    try:
        rubrique = get_object_or_404(RubriquePersonnalisee, id=rubrique_id)
        
        # Vérifier s'il y a des assignations actives
        assignations_actives = EmployeRubrique.objects.filter(
            rubrique=rubrique,
            actif=True
        ).count()
        
        if assignations_actives > 0:
            # Désactiver au lieu de supprimer
            rubrique.actif = False
            rubrique.date_modification = timezone.now()
            rubrique.save()
            
            # Désactiver aussi les assignations
            EmployeRubrique.objects.filter(rubrique=rubrique).update(actif=False)
            
            return JsonResponse({
                'success': True,
                'message': f'Rubrique "{rubrique.nom}" désactivée (utilisée par {assignations_actives} employé(s))'
            })
        else:
            # Suppression réelle si pas d'assignations
            nom_rubrique = rubrique.nom
            rubrique.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Rubrique "{nom_rubrique}" supprimée définitivement'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@login_required
@admin_required
@require_POST
def tester_formule_ajax(request):
    """
    Tester une formule de calcul de rubrique
    """
    try:
        data = json.loads(request.body)
        formule = data.get('formule', '').strip()
        
        if not formule:
            return JsonResponse({
                'success': False,
                'erreur': 'Formule vide'
            })
        
        # Variables de test pour validation
        variables_test = {
            'salaire_base': Decimal('5000'),
            'heures_travaillees': Decimal('173.33'),
            'jours_travailles': 22,
            'anciennete_mois': 24,
            'coefficient': Decimal('1.2'),
        }
        
        # Essayer d'évaluer la formule
        try:
            # Remplacer les variables dans la formule
            formule_evaluable = formule
            for var, valeur in variables_test.items():
                formule_evaluable = formule_evaluable.replace(var, str(valeur))
            
            # Évaluation sécurisée (attention aux risques de sécurité en production)
            resultat = eval(formule_evaluable)
            
            return JsonResponse({
                'success': True,
                'resultat': f'{float(resultat):.2f} DH',
                'formule_testee': formule,
                'variables_utilisees': variables_test
            })
            
        except Exception as eval_error:
            return JsonResponse({
                'success': False,
                'erreur': f'Erreur dans la formule: {str(eval_error)}',
                'formule': formule
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'erreur': f'Erreur de traitement: {str(e)}'
        })


@login_required
@admin_required
def assigner_employes_ajax(request, rubrique_id):
    """
    Gérer l'assignation d'une rubrique aux employés
    """
    rubrique = get_object_or_404(RubriquePersonnalisee, id=rubrique_id)
    
    if request.method == 'GET':
        # Retourner la liste des employés avec leur statut d'assignation
        employes = Employe.objects.filter(actif=True).select_related('user', 'site')
        
        employes_data = []
        for employe in employes:
            assignation = EmployeRubrique.objects.filter(
                employe=employe,
                rubrique=rubrique,
                actif=True
            ).first()
            
            employes_data.append({
                'id': employe.id,
                'nom': employe.nom,
                'prenom': employe.prenom,
                'initiales': f"{employe.prenom[0] if employe.prenom else ''}{employe.nom[0] if employe.nom else ''}",
                'fonction': employe.fonction,
                'site': employe.site.nom if employe.site else None,
                'assigned': assignation is not None,
                'valeur': float(assignation.valeur) if assignation and assignation.valeur else ''
            })
        
        return JsonResponse({
            'success': True,
            'employes': employes_data,
            'rubrique': {
                'id': rubrique.id,
                'nom': rubrique.nom,
                'code': rubrique.code
            }
        })
    
    elif request.method == 'POST':
        # Sauvegarder les assignations
        try:
            data = json.loads(request.body)
            assignations = data.get('assignations', [])
            
            # Désactiver toutes les assignations existantes
            EmployeRubrique.objects.filter(rubrique=rubrique).update(actif=False)
            
            # Créer/réactiver les nouvelles assignations
            nouvelles_assignations = 0
            for assignation in assignations:
                employe_id = assignation.get('employe_id')
                valeur = assignation.get('valeur')
                
                employe = get_object_or_404(Employe, id=employe_id)
                
                # Essayer de réactiver une assignation existante
                obj_assignation, created = EmployeRubrique.objects.get_or_create(
                    employe=employe,
                    rubrique=rubrique,
                    defaults={
                        'valeur': Decimal(str(valeur)) if valeur else None,
                        'actif': True,
                        'cree_par': request.user
                    }
                )
                
                if not created:
                    obj_assignation.valeur = Decimal(str(valeur)) if valeur else None
                    obj_assignation.actif = True
                    obj_assignation.save()
                
                nouvelles_assignations += 1
            
            return JsonResponse({
                'success': True,
                'message': f'{nouvelles_assignations} assignation(s) enregistrée(s) pour "{rubrique.nom}"'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur lors de la sauvegarde: {str(e)}'
            })
