"""
Logique de calcul de paie selon la législation marocaine - Version avec intégration absences
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from django.utils import timezone
from django.db import models
from django.db.models import Q
from .models import Employe, ElementPaie, ParametrePaie, BulletinPaie, Absence


class CalculateurPaie:
    """
    Calculateur de paie selon la législation marocaine 2025
    """
    
    def __init__(self):
        # Paramètres par défaut selon la législation marocaine
        self.TAUX_CNSS_SALARIE = Decimal('4.48')  # 4.48%
        self.TAUX_AMO_SALARIE = Decimal('2.26')   # 2.26%
        self.TAUX_CIMR = Decimal('6.00')          # 6.00%
        self.FRAIS_PROFESSIONNELS = Decimal('20.00')  # 20%
        
        # Plafonds CNSS (en DH mensuels)
        self.PLAFOND_CNSS = Decimal('6000.00')
        
        # Paramètres de calcul d'absence
        self.JOURS_OUVRABLES_MOIS = Decimal('26')  # Base de calcul standard
        
        # Barème IR 2025 - Tranches mensuelles (simplifié)
        self.BAREME_IR = [
            {'min': Decimal('0'), 'max': Decimal('2500'), 'taux': Decimal('0')},
            {'min': Decimal('2500'), 'max': Decimal('4166.67'), 'taux': Decimal('10')},
            {'min': Decimal('4166.67'), 'max': Decimal('5000'), 'taux': Decimal('20')},
            {'min': Decimal('5000'), 'max': Decimal('6666.67'), 'taux': Decimal('30')},
            {'min': Decimal('6666.67'), 'max': Decimal('15000'), 'taux': Decimal('34')},
            {'min': Decimal('15000'), 'max': None, 'taux': Decimal('38')}
        ]
        
        # Déductions pour enfants à charge (par enfant par mois)
        self.DEDUCTION_ENFANT = Decimal('30.00')
    
    def arrondir(self, montant):
        """Arrondir un montant à 2 décimales"""
        if montant is None:
            return Decimal('0.00')
        return Decimal(str(montant)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculer_elements_paie(self, employe, mois, annee):
        """
        Calcule les éléments de paie (primes, retenues, etc.)
        """
        try:
            elements = ElementPaie.objects.filter(
                employe=employe,
                mois_application=mois,
                annee_application=annee
            )
            
            primes = Decimal('0')
            retenues = Decimal('0')
            avances = Decimal('0')
            heures_sup = Decimal('0')
            
            for element in elements:
                if element.type_element == 'PRIME':
                    primes += self.arrondir(element.montant)
                elif element.type_element == 'RETENUE':
                    retenues += self.arrondir(element.montant)
                elif element.type_element == 'AVANCE':
                    avances += self.arrondir(element.montant)
                elif element.type_element == 'HEURES_SUP':
                    heures_sup += self.arrondir(element.montant)
            
            return {
                'primes': primes,
                'retenues': retenues,
                'avances': avances,
                'heures_sup': heures_sup,
            }
        except Exception:
            # En cas d'erreur, retourner des zéros
            return {
                'primes': Decimal('0'),
                'retenues': Decimal('0'),
                'avances': Decimal('0'),
                'heures_sup': Decimal('0'),
            }
    
    def calculer_absences(self, employe, mois, annee):
        """
        Calcule l'impact des absences sur le salaire - VERSION AMÉLIORÉE
        """
        try:
            # Récupérer toutes les absences du mois qui sont approuvées
            absences = Absence.objects.filter(
                employe=employe,
                statut='APPROUVE'
            )
            
            # Filtrer les absences qui touchent le mois demandé
            absences_du_mois = []
            
            for absence in absences:
                # Vérifier si l'absence touche le mois/année demandé
                if (absence.date_debut.month == mois and absence.date_debut.year == annee) or \
                   (absence.date_fin.month == mois and absence.date_fin.year == annee) or \
                   (absence.date_debut.month < mois and absence.date_fin.month > mois and absence.date_debut.year <= annee and absence.date_fin.year >= annee):
                    absences_du_mois.append(absence)
            
            # Calculer le total des jours d'absence impactant le salaire
            total_jours_deduction = 0
            absences_details = []
            
            for absence in absences_du_mois:
                if absence.impact_salaire:  # Seulement les absences sans solde
                    # Calculer les jours qui tombent dans le mois demandé
                    from datetime import date
                    
                    # Dates de début et fin du mois
                    debut_mois = date(annee, mois, 1)
                    if mois == 12:
                        fin_mois = date(annee + 1, 1, 1)
                    else:
                        fin_mois = date(annee, mois + 1, 1)
                    fin_mois = date(fin_mois.year, fin_mois.month, fin_mois.day - 1)
                    
                    # Intersection entre la période d'absence et le mois
                    debut_effective = max(absence.date_debut, debut_mois)
                    fin_effective = min(absence.date_fin, fin_mois)
                    
                    if debut_effective <= fin_effective:
                        jours_dans_mois = (fin_effective - debut_effective).days + 1
                        total_jours_deduction += jours_dans_mois
                        
                        absences_details.append({
                            'type': absence.get_type_absence_display(),
                            'debut': debut_effective,
                            'fin': fin_effective,
                            'jours': jours_dans_mois,
                            'motif': absence.motif
                        })
            
            # Calcul de la déduction financière
            if total_jours_deduction > 0:
                salaire_journalier = employe.salaire_base / self.JOURS_OUVRABLES_MOIS
                deduction_totale = salaire_journalier * Decimal(str(total_jours_deduction))
                
                return {
                    'deduction_montant': self.arrondir(deduction_totale),
                    'jours_deduits': total_jours_deduction,
                    'salaire_journalier': self.arrondir(salaire_journalier),
                    'absences_details': absences_details
                }
            
            return {
                'deduction_montant': Decimal('0'),
                'jours_deduits': 0,
                'salaire_journalier': self.arrondir(employe.salaire_base / self.JOURS_OUVRABLES_MOIS),
                'absences_details': []
            }
            
        except Exception as e:
            # En cas d'erreur, ne pas décompter mais logger l'erreur
            print(f"Erreur calcul absences pour {employe.nom_complet()}: {str(e)}")
            return {
                'deduction_montant': Decimal('0'),
                'jours_deduits': 0,
                'salaire_journalier': Decimal('0'),
                'absences_details': [],
                'erreur': str(e)
            }
    
    def calculer_cotisation_cnss(self, salaire_brut_imposable):
        """
        Calcule la cotisation CNSS (plafonnée à 6000 DH)
        """
        assiette = min(salaire_brut_imposable, self.PLAFOND_CNSS)
        cotisation = assiette * (self.TAUX_CNSS_SALARIE / Decimal('100'))
        return self.arrondir(cotisation)
    
    def calculer_cotisation_amo(self, salaire_brut_imposable):
        """
        Calcule la cotisation AMO (non plafonnée)
        """
        cotisation = salaire_brut_imposable * (self.TAUX_AMO_SALARIE / Decimal('100'))
        return self.arrondir(cotisation)
    
    def calculer_cotisation_cimr(self, salaire_brut_imposable):
        """
        Calcule la cotisation CIMR
        """
        cotisation = salaire_brut_imposable * (self.TAUX_CIMR / Decimal('100'))
        return self.arrondir(cotisation)
    
    def calculer_impot_revenu(self, salaire_brut_imposable, nombre_enfants):
        """
        Calcule l'impôt sur le revenu selon le barème marocain
        """
        # Déduction des frais professionnels (20%)
        frais_pro = salaire_brut_imposable * (self.FRAIS_PROFESSIONNELS / Decimal('100'))
        
        # Base imposable après frais professionnels
        base_imposable = salaire_brut_imposable - frais_pro
        
        # Déduction pour enfants à charge
        deduction_enfants = Decimal(str(nombre_enfants)) * self.DEDUCTION_ENFANT
        base_imposable -= deduction_enfants
        
        # Si la base est négative ou nulle, pas d'impôt
        if base_imposable <= 0:
            return Decimal('0')
        
        # Calcul simple par tranches
        impot = Decimal('0')
        
        if base_imposable <= Decimal('2500'):
            impot = Decimal('0')
        elif base_imposable <= Decimal('4166.67'):
            impot = (base_imposable - Decimal('2500')) * Decimal('0.10')
        elif base_imposable <= Decimal('5000'):
            impot = Decimal('166.67') + (base_imposable - Decimal('4166.67')) * Decimal('0.20')
        elif base_imposable <= Decimal('6666.67'):
            impot = Decimal('333.33') + (base_imposable - Decimal('5000')) * Decimal('0.30')
        elif base_imposable <= Decimal('15000'):
            impot = Decimal('833.33') + (base_imposable - Decimal('6666.67')) * Decimal('0.34')
        else:
            impot = Decimal('3666.67') + (base_imposable - Decimal('15000')) * Decimal('0.38')
        
        return self.arrondir(impot)

    def calculer_rubriques_personnalisees(self, employe, mois, annee):
        """
        Calcule les rubriques personnalisées pour un employé
        """
        try:
            from .models import EmployeRubrique
            from datetime import date

            # Date de référence pour le calcul
            date_calcul = date(annee, mois, 1)

            # Récupérer les rubriques actives pour cet employé
            rubriques_employe = EmployeRubrique.objects.filter(
                employe=employe,
                actif=True,
                date_debut__lte=date_calcul,
                rubrique__actif=True
            ).filter(
                models.Q(date_fin__isnull=True) | models.Q(date_fin__gte=date_calcul)
            ).select_related('rubrique')

            # Séparer les éléments par type
            gains_supplementaires = Decimal('0')
            retenues_supplementaires = Decimal('0')
            cotisations_speciales = Decimal('0')
            allocations = Decimal('0')

            # Détails pour le rapport
            details_rubriques = []

            for rubrique_employe in rubriques_employe:
                rubrique = rubrique_employe.rubrique

                # Calculer le montant (on utilisera le salaire de base pour l'instant)
                montant = rubrique_employe.calculer_montant(
                    employe.salaire_base,
                    employe.salaire_base
                )

                if montant > 0:
                    # Classer selon le type de rubrique
                    if rubrique.type_rubrique == 'GAIN':
                        gains_supplementaires += montant
                    elif rubrique.type_rubrique == 'RETENUE':
                        retenues_supplementaires += montant
                    elif rubrique.type_rubrique == 'COTISATION':
                        cotisations_speciales += montant
                    elif rubrique.type_rubrique == 'ALLOCATION':
                        allocations += montant
                    elif rubrique.type_rubrique in ['TRANSPORT', 'FORMATION', 'MEDICAL']:
                        gains_supplementaires += montant

                    # Ajouter aux détails
                    details_rubriques.append({
                        'code': rubrique.code,
                        'nom': rubrique.nom,
                        'type': rubrique.get_type_rubrique_display(),
                        'montant': montant,
                        'soumis_ir': rubrique.soumis_ir,
                        'soumis_cnss': rubrique.soumis_cnss,
                        'soumis_amo': rubrique.soumis_amo,
                    })

            return {
                'gains_supplementaires': gains_supplementaires,
                'retenues_supplementaires': retenues_supplementaires,
                'cotisations_speciales': cotisations_speciales,
                'allocations': allocations,
                'details_rubriques': details_rubriques,
                'total_impact_positif': gains_supplementaires + allocations,
                'total_impact_negatif': retenues_supplementaires + cotisations_speciales
            }

        except Exception as e:
            print(f"Erreur calcul rubriques personnalisées pour {employe.nom_complet()}: {str(e)}")
            return {
                'gains_supplementaires': Decimal('0'),
                'retenues_supplementaires': Decimal('0'),
                'cotisations_speciales': Decimal('0'),
                'allocations': Decimal('0'),
                'details_rubriques': [],
                'total_impact_positif': Decimal('0'),
                'total_impact_negatif': Decimal('0'),
                'erreur': str(e)
            }
def calculer_bulletin_complet(self, employe, mois, annee):
    """
    Calcul complet d'un bulletin de paie avec intégration des rubriques personnalisées
    Version améliorée avec support des rubriques personnalisées
    """
    from decimal import Decimal
    from .models import BulletinPaie, ElementPaie
    
    # 1. Calculs de base (existants)
    salaire_base = employe.salaire_base
    heures_supp = self.calculer_heures_supplementaires(employe, mois, annee)
    absences_info = self.calculer_absences(employe, mois, annee)
    
    # 2. NOUVEAU : Calcul des rubriques personnalisées
    rubriques_info = employe.calculer_rubriques_personnalisees(
        mois, annee, salaire_base, salaire_base
    )
    
    # 3. Calcul du salaire brut avec rubriques
    salaire_brut_base = salaire_base + heures_supp['montant'] - absences_info['montant_deduit']
    salaire_brut_avec_gains = salaire_brut_base + rubriques_info['total_gains']
    
    # Les allocations ne sont pas soumises aux cotisations dans la plupart des cas
    salaire_brut_imposable = salaire_brut_avec_gains
    salaire_brut_non_imposable = rubriques_info['total_allocations']
    
    # 4. Recalculer les rubriques avec le salaire brut définitif
    # (pour les rubriques en pourcentage du brut)
    rubriques_info_finale = employe.calculer_rubriques_personnalisees(
        mois, annee, salaire_base, salaire_brut_imposable
    )
    
    # 5. Calculs des cotisations (sur salaire brut imposable uniquement)
    cotisations = self.calculer_cotisations_sociales(salaire_brut_imposable)
    impot = self.calculer_impot_revenu(salaire_brut_imposable, cotisations, employe)
    
    # 6. Calcul final avec retenues personnalisées
    total_retenues = (
        cotisations['total'] + 
        impot + 
        rubriques_info_finale['total_retenues'] + 
        rubriques_info_finale['total_cotisations']
    )
    
    salaire_net = salaire_brut_imposable - total_retenues
    net_a_payer = salaire_net + salaire_brut_non_imposable
    
    # 7. Créer ou mettre à jour le bulletin
    bulletin, created = BulletinPaie.objects.get_or_create(
        employe=employe,
        mois=mois,
        annee=annee,
        defaults={
            'salaire_base': salaire_base,
            'salaire_brut_imposable': salaire_brut_imposable,
            'salaire_brut_non_imposable': salaire_brut_non_imposable,
            'cotisation_cnss': cotisations['cnss'],
            'cotisation_amo': cotisations['amo'],
            'cotisation_cimr': cotisations['cimr'],
            'impot_revenu': impot,
            'salaire_net': salaire_net,
            'net_a_payer': net_a_payer,
            'heures_supplementaires': heures_supp['heures'],
            'montant_heures_supp': heures_supp['montant'],
            'jours_absence': absences_info['jours_deduits'],
            'montant_absences': absences_info['montant_deduit'],
            'total_primes': rubriques_info_finale['total_gains'],
            'total_retenues': rubriques_info_finale['total_retenues'] + rubriques_info_finale['total_cotisations'],
            'total_allocations': rubriques_info_finale['total_allocations']
        }
    )
    
    # Mettre à jour si existant
    if not created:
        bulletin.salaire_base = salaire_base
        bulletin.salaire_brut_imposable = salaire_brut_imposable
        bulletin.salaire_brut_non_imposable = salaire_brut_non_imposable
        bulletin.cotisation_cnss = cotisations['cnss']
        bulletin.cotisation_amo = cotisations['amo']
        bulletin.cotisation_cimr = cotisations['cimr']
        bulletin.impot_revenu = impot
        bulletin.salaire_net = salaire_net
        bulletin.net_a_payer = net_a_payer
        bulletin.heures_supplementaires = heures_supp['heures']
        bulletin.montant_heures_supp = heures_supp['montant']
        bulletin.jours_absence = absences_info['jours_deduits']
        bulletin.montant_absences = absences_info['montant_deduit']
        bulletin.total_primes = rubriques_info_finale['total_gains']
        bulletin.total_retenues = rubriques_info_finale['total_retenues'] + rubriques_info_finale['total_cotisations']
        bulletin.total_allocations = rubriques_info_finale['total_allocations']
        bulletin.save()
    
    # 8. NOUVEAU : Créer les éléments de paie pour les rubriques personnalisées
    self._creer_elements_rubriques_personnalisees(bulletin, rubriques_info_finale)
    
    return {
        'bulletin': bulletin,
        'details': {
            'salaire_base': salaire_base,
            'heures_supp': heures_supp,
            'absences': absences_info,
            'rubriques': rubriques_info_finale,
            'cotisations': cotisations,
            'impot': impot,
            'salaire_net': salaire_net,
            'net_a_payer': net_a_payer
        }
    }

# 2. NOUVELLE MÉTHODE : Créer les éléments de paie pour les rubriques
def _creer_elements_rubriques_personnalisees(self, bulletin, rubriques_info):
    """
    Crée les éléments de paie pour chaque rubrique personnalisée calculée
    """
    from .models import ElementPaie
    
    # Supprimer les anciens éléments de rubriques personnalisées
    ElementPaie.objects.filter(
        bulletin=bulletin,
        type_element__in=['RUBRIQUE_GAIN', 'RUBRIQUE_RETENUE', 'RUBRIQUE_ALLOCATION', 'RUBRIQUE_COTISATION']
    ).delete()
    
    # Créer les nouveaux éléments
    elements_a_creer = []
    
    # Gains
    for rubrique, montant in rubriques_info['gains']:
        elements_a_creer.append(ElementPaie(
            bulletin=bulletin,
            type_element='RUBRIQUE_GAIN',
            libelle=rubrique.nom,
            code=rubrique.code,
            base_calcul=bulletin.salaire_base,
            taux=rubrique.pourcentage if rubrique.mode_calcul == 'POURCENTAGE' else None,
            montant=montant,
            soumis_ir=rubrique.soumis_ir,
            soumis_cnss=rubrique.soumis_cnss,
            commentaire=f"Rubrique personnalisée: {rubrique.description}"
        ))
    
    # Retenues
    for rubrique, montant in rubriques_info['retenues']:
        elements_a_creer.append(ElementPaie(
            bulletin=bulletin,
            type_element='RUBRIQUE_RETENUE',
            libelle=rubrique.nom,
            code=rubrique.code,
            base_calcul=bulletin.salaire_base,
            taux=rubrique.pourcentage if rubrique.mode_calcul == 'POURCENTAGE' else None,
            montant=montant,
            soumis_ir=rubrique.soumis_ir,
            soumis_cnss=rubrique.soumis_cnss,
            commentaire=f"Rubrique personnalisée: {rubrique.description}"
        ))
    
    # Allocations
    for rubrique, montant in rubriques_info['allocations']:
        elements_a_creer.append(ElementPaie(
            bulletin=bulletin,
            type_element='RUBRIQUE_ALLOCATION',
            libelle=rubrique.nom,
            code=rubrique.code,
            base_calcul=None,  # Les allocations ne dépendent généralement pas du salaire
            taux=None,
            montant=montant,
            soumis_ir=rubrique.soumis_ir,
            soumis_cnss=rubrique.soumis_cnss,
            commentaire=f"Rubrique personnalisée: {rubrique.description}"
        ))
    
    # Cotisations spéciales
    for rubrique, montant in rubriques_info['cotisations']:
        elements_a_creer.append(ElementPaie(
            bulletin=bulletin,
            type_element='RUBRIQUE_COTISATION',
            libelle=rubrique.nom,
            code=rubrique.code,
            base_calcul=bulletin.salaire_base,
            taux=rubrique.pourcentage if rubrique.mode_calcul == 'POURCENTAGE' else None,
            montant=montant,
            soumis_ir=rubrique.soumis_ir,
            soumis_cnss=rubrique.soumis_cnss,
            commentaire=f"Rubrique personnalisée: {rubrique.description}"
        ))
    
    # Création en lot pour optimiser les performances
    if elements_a_creer:
        ElementPaie.objects.bulk_create(elements_a_creer)

# 3. NOUVELLE MÉTHODE : Récupérer le détail des rubriques pour affichage
def get_detail_rubriques_personnalisees(self, employe, mois, annee):
    """
    Retourne le détail formaté des rubriques personnalisées pour l'affichage
    """
    rubriques_info = employe.calculer_rubriques_personnalisees(
        mois, annee, employe.salaire_base, employe.salaire_base
    )
    
    detail = {
        'gains': [],
        'retenues': [],
        'allocations': [],
        'cotisations': []
    }
    
    for rubrique, montant in rubriques_info['gains']:
        detail['gains'].append({
            'code': rubrique.code,
            'nom': rubrique.nom,
            'montant': montant,
            'description': rubrique.description,
            'soumis_ir': rubrique.soumis_ir,
            'soumis_cnss': rubrique.soumis_cnss
        })
    
    # Répéter pour retenues, allocations, cotisations...
    for rubrique, montant in rubriques_info['retenues']:
        detail['retenues'].append({
            'code': rubrique.code,
            'nom': rubrique.nom,
            'montant': montant,
            'description': rubrique.description,
            'soumis_ir': rubrique.soumis_ir,
            'soumis_cnss': rubrique.soumis_cnss
        })
    
    for rubrique, montant in rubriques_info['allocations']:
        detail['allocations'].append({
            'code': rubrique.code,
            'nom': rubrique.nom,
            'montant': montant,
            'description': rubrique.description,
            'soumis_ir': rubrique.soumis_ir,
            'soumis_cnss': rubrique.soumis_cnss
        })
    
    for rubrique, montant in rubriques_info['cotisations']:
        detail['cotisations'].append({
            'code': rubrique.code,
            'nom': rubrique.nom,
            'montant': montant,
            'description': rubrique.description,
            'soumis_ir': rubrique.soumis_ir,
            'soumis_cnss': rubrique.soumis_cnss
        })
    
    return detail
   
    def generer_bulletin(self, employe, mois, annee, utilisateur=None):
        """
        Génère et sauvegarde un bulletin de paie - AVEC ABSENCES
        """
        # Calculer le bulletin
        bulletin_data = self.calculer_bulletin_complet(employe, mois, annee)
        
        # Créer ou mettre à jour le bulletin
        bulletin, created = BulletinPaie.objects.update_or_create(
            employe=employe,
            mois=mois,
            annee=annee,
            defaults={
                'salaire_base': bulletin_data['salaire_base'],
                'heures_travaillees': bulletin_data['heures_travaillees'],
                'heures_supplementaires': bulletin_data['heures_supplementaires'],
                'total_primes': bulletin_data['total_primes'],
                'total_retenues': bulletin_data['total_retenues'],
                'total_avances': bulletin_data['total_avances'],
                'salaire_brut_imposable': bulletin_data['salaire_brut_imposable'],
                'salaire_brut_non_imposable': bulletin_data['salaire_brut_non_imposable'],
                'cotisation_cnss': bulletin_data['cotisation_cnss'],
                'cotisation_amo': bulletin_data['cotisation_amo'],
                'cotisation_cimr': bulletin_data['cotisation_cimr'],
                'impot_revenu': bulletin_data['impot_revenu'],
                'salaire_net': bulletin_data['salaire_net'],
                'net_a_payer': bulletin_data['net_a_payer'],
                'calcule_par': utilisateur,
                'valide': False,
                'envoye': False
            }
        )
        
        # **NOUVEAU : Stocker les informations d'absences dans les notes ou logs**
        if bulletin_data['jours_absence'] > 0:
            print(f"✅ Bulletin {employe.nom_complet()} : {bulletin_data['jours_absence']} jours d'absence déduits ({bulletin_data['deduction_absences']} DH)")
        
        return bulletin
    
    def calculer_paie_massive(self, employes, mois, annee, utilisateur=None):
        """
        Calcule la paie pour plusieurs employés - AVEC RAPPORTS ABSENCES
        """
        bulletins_crees = []
        erreurs = []
        rapport_absences = []
        
        for employe in employes:
            try:
                bulletin = self.generer_bulletin(employe, mois, annee, utilisateur)
                bulletins_crees.append(bulletin)
                
                # Ajouter info sur les absences pour le rapport
                absences_info = self.calculer_absences(employe, mois, annee)
                if absences_info['jours_deduits'] > 0:
                    rapport_absences.append({
                        'employe': employe.nom_complet(),
                        'matricule': employe.matricule,
                        'jours_deduits': absences_info['jours_deduits'],
                        'montant_deduit': absences_info['deduction_montant'],
                        'details': absences_info['absences_details']
                    })
                    
            except Exception as e:
                erreurs.append({
                    'employe': employe,
                    'erreur': str(e)
                })
        
        return {
            'bulletins_crees': bulletins_crees,
            'erreurs': erreurs,
            'total_traite': len(employes),
            'total_reussi': len(bulletins_crees),
            'total_erreurs': len(erreurs),
            'rapport_absences': rapport_absences  # **NOUVEAU**
        }