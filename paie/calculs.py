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
        Calcule un bulletin de paie complet pour un employé - AVEC INTÉGRATION ABSENCES
        """
        # Salaire de base
        salaire_base = self.arrondir(employe.salaire_base)
        
        # Éléments de paie
        elements = self.calculer_elements_paie(employe, mois, annee)
        
        # **NOUVEAU : Calcul des absences**
        absences_info = self.calculer_absences(employe, mois, annee)
        deduction_absences = absences_info['deduction_montant']
        
        rubriques_info = self.calculer_rubriques_personnalisees(employe, mois, annee)
        
        # Salaire brut imposable (après déduction des absences + rubriques)
        salaire_brut_imposable = (
            salaire_base + 
            elements['primes'] + 
            elements['heures_sup'] +
            rubriques_info['gains_supplementaires'] +
            rubriques_info['allocations'] -
            deduction_absences -
            rubriques_info['retenues_supplementaires']
        )
        # S'assurer que le salaire brut ne soit pas négatif
        if salaire_brut_imposable < 0:
            salaire_brut_imposable = Decimal('0')
        
        # Calcul des cotisations sociales (sur le brut après absences)
        cnss = self.calculer_cotisation_cnss(salaire_brut_imposable)
        amo = self.calculer_cotisation_amo(salaire_brut_imposable)
        cimr = self.calculer_cotisation_cimr(salaire_brut_imposable)
        
        # Calcul de l'impôt sur le revenu (sur le brut après absences)
        ir = self.calculer_impot_revenu(salaire_brut_imposable, employe.nombre_enfants)
        
        # Calcul du net à payer
        total_cotisations = cnss + amo + cimr
        total_deductions = (
            total_cotisations + 
            ir + 
            elements['retenues'] + 
            elements['avances'] +
            rubriques_info['cotisations_speciales']
        )
        
        
        net_a_payer = salaire_brut_imposable - total_deductions
        
        # S'assurer que le net à payer ne soit pas négatif
        if net_a_payer < 0:
            net_a_payer = Decimal('0')
        
        return {
            'employe': employe,
            'mois': mois,
            'annee': annee,
            'salaire_base': salaire_base,
            'heures_travaillees': 191,  # Standard
            'heures_supplementaires': elements['heures_sup'],
            'total_primes': elements['primes'],
            'total_retenues': elements['retenues'],
            'total_avances': elements['avances'],
            
            # **NOUVELLES DONNÉES ABSENCES**
            'deduction_absences': deduction_absences,
            'jours_absence': absences_info['jours_deduits'],
            'absences_details': absences_info['absences_details'],
            
            'salaire_brut_imposable': salaire_brut_imposable,
            'salaire_brut_non_imposable': Decimal('0'),
            'cotisation_cnss': cnss,
            'cotisation_amo': amo,
            'cotisation_cimr': cimr,
            'impot_revenu': ir,
            'salaire_net': salaire_brut_imposable - total_cotisations - ir,
            'net_a_payer': self.arrondir(net_a_payer),
            'total_cotisations': total_cotisations,
            'total_deductions': total_deductions,
             'rubriques_gains': rubriques_info['gains_supplementaires'],
            'rubriques_retenues': rubriques_info['retenues_supplementaires'],
            'rubriques_allocations': rubriques_info['allocations'],
            'rubriques_cotisations': rubriques_info['cotisations_speciales'],
            'rubriques_details': rubriques_info['details_rubriques'],
        }
    
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