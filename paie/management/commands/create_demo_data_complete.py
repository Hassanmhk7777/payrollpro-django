from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from paie.models import Employe, Site, Departement, Absence, RubriquePersonnalisee, EmployeRubrique
from datetime import datetime, timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Créer des données de démonstration réalistes pour PayrollPro'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Création des données de démonstration PayrollPro...'))

        # Créer les groupes d'utilisateurs s'ils n'existent pas
        self.create_user_groups()
        
        # Créer des sites réalistes
        self.create_sites()
        
        # Créer des départements
        self.create_departments()
        
        # Créer des employés avec des données réalistes
        self.create_employees()
        
        # Créer des rubriques personnalisées réalistes
        self.create_custom_rubriques()
        
        # Assigner des rubriques aux employés
        self.assign_rubriques_to_employees()
        
        # Créer quelques absences
        self.create_absences()
        
        self.stdout.write(self.style.SUCCESS('✅ Données de démonstration créées avec succès!'))

    def create_user_groups(self):
        """Créer les groupes d'utilisateurs"""
        groups = ['Admin', 'RH', 'Employe']
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
        self.stdout.write(f'👥 Groupes d\'utilisateurs créés')

    def create_sites(self):
        """Créer des sites avec données complètes"""
        self.site1, created = Site.objects.get_or_create(
            code='CAS',
            defaults={
                'nom': 'Siège Social Casablanca',
                'raison_sociale': 'PayrollPro SARL',
                'forme_juridique': 'SARL',
                'numero_rc': 'RC123456',
                'numero_cnss': 'CNSS789012',
                'numero_patente': 'PAT345678',
                'ice': '002345678901234',
                'adresse': 'Boulevard Mohammed V, Twin Center, Casablanca',
                'ville': 'Casablanca',
                'code_postal': '20100',
                'telephone': '+212 522 123 456',
                'email': 'contact@payrollpro.ma',
                'directeur_general': 'Ahmed BENALI',
                'directeur_rh': 'Fatima ALAOUI',
                'actif': True
            }
        )
        
        self.site2, created = Site.objects.get_or_create(
            code='RAB',
            defaults={
                'nom': 'Filiale Rabat',
                'raison_sociale': 'PayrollPro SARL - Filiale Rabat',
                'forme_juridique': 'Filiale',
                'numero_rc': 'RC654321',
                'numero_cnss': 'CNSS210987',
                'adresse': 'Avenue Hassan II, Agdal, Rabat',
                'ville': 'Rabat',
                'code_postal': '10000',
                'telephone': '+212 537 654 321',
                'email': 'rabat@payrollpro.ma',
                'directeur_general': 'Omar FASSI',
                'directeur_rh': 'Aicha BENALI',
                'actif': True
            }
        )
        self.stdout.write(f'🏢 Sites créés: {self.site1.nom}, {self.site2.nom}')

    def create_departments(self):
        """Créer des départements réalistes"""
        departments_data = [
            ('RH', 'Ressources Humaines', self.site1),
            ('IT', 'Informatique', self.site1),
            ('COMPTA', 'Comptabilité', self.site1),
            ('VENTE', 'Commercial', self.site1),
            ('PROD', 'Production', self.site1),
            ('ADMIN', 'Administration', self.site2),
            ('LOG', 'Logistique', self.site2),
        ]
        
        self.departments = {}
        for code, nom, site in departments_data:
            dept, created = Departement.objects.get_or_create(
                code=code,
                site=site,
                defaults={'nom': nom, 'actif': True}
            )
            self.departments[code] = dept
        
        self.stdout.write(f'🏬 Départements créés: {len(self.departments)}')

    def create_employees(self):
        """Créer des employés avec des salaires réalistes"""
        employees_data = [
            # Admin
            ('admin', 'Administrateur', 'Système', 'admin@payrollpro.ma', 'Admin', 'IT', 15000, 'Administrateur système'),
            
            # RH
            ('drh', 'Fatima', 'ALAOUI', 'f.alaoui@payrollpro.ma', 'RH', 'RH', 12000, 'Directrice RH'),
            ('rh1', 'Zakaria', 'BERRADA', 'z.berrada@payrollpro.ma', 'RH', 'RH', 8000, 'Responsable RH'),
            ('rh2', 'Nadia', 'BENNANI', 'n.bennani@payrollpro.ma', 'RH', 'RH', 6500, 'Assistante RH'),
            
            # IT
            ('dev1', 'Mehdi', 'CHAKIR', 'm.chakir@payrollpro.ma', 'Employe', 'IT', 9500, 'Développeur Senior'),
            ('dev2', 'Sara', 'AMRANI', 's.amrani@payrollpro.ma', 'Employe', 'IT', 7500, 'Développeuse'),
            ('sys1', 'Youssef', 'MOUNIR', 'y.mounir@payrollpro.ma', 'Employe', 'IT', 8500, 'Administrateur réseau'),
            
            # Comptabilité
            ('comptable1', 'Rachid', 'JILALI', 'r.jilali@payrollpro.ma', 'Employe', 'COMPTA', 7000, 'Comptable'),
            ('comptable2', 'Laila', 'OUALI', 'l.ouali@payrollpro.ma', 'Employe', 'COMPTA', 6000, 'Aide-comptable'),
            
            # Commercial
            ('comm1', 'Hassan', 'TAZI', 'h.tazi@payrollpro.ma', 'Employe', 'VENTE', 8000, 'Responsable commercial'),
            ('comm2', 'Imane', 'BOUHALI', 'i.bouhali@payrollpro.ma', 'Employe', 'VENTE', 5500, 'Commerciale'),
            
            # Production
            ('prod1', 'Abdellah', 'RHALI', 'a.rhali@payrollpro.ma', 'Employe', 'PROD', 5000, 'Chef d\'équipe'),
            ('prod2', 'Khadija', 'MANSOURI', 'k.mansouri@payrollpro.ma', 'Employe', 'PROD', 4200, 'Opératrice'),
        ]
        
        self.employees = {}
        for username, prenom, nom, email, role, dept_code, salaire, fonction in employees_data:
            # Créer l'utilisateur
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': prenom,
                    'last_name': nom,
                    'email': email,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('demo123')  # Mot de passe par défaut
                user.save()
                
                # Ajouter au groupe approprié
                group = Group.objects.get(name=role)
                user.groups.add(group)
            
            # Créer l'employé
            employe, created = Employe.objects.get_or_create(
                user=user,
                defaults={
                    'matricule': username.upper(),  # Utiliser le username comme matricule
                    'nom': nom,
                    'prenom': prenom,
                    'cin': f'CIN{random.randint(100000, 999999)}',  # CIN fictif
                    'email': email,
                    'fonction': fonction,
                    'salaire_base': Decimal(str(salaire)),
                    'site': self.site1 if dept_code in ['RH', 'IT', 'COMPTA', 'VENTE', 'PROD'] else self.site2,
                    'departement': self.departments.get(dept_code),
                    'date_embauche': datetime.now().date() - timedelta(days=random.randint(30, 1800)),
                    'actif': True,
                }
            )
            self.employees[username] = employe
        
        self.stdout.write(f'👥 Employés créés: {len(self.employees)}')

    def create_custom_rubriques(self):
        """Créer des rubriques personnalisées réalistes"""
        rubriques_data = [
            # Gains
            ('PRIME_PERF', 'Prime de Performance', 'GAIN', 'salaire_base * 0.1', 'Prime mensuelle de performance', True, 10),
            ('PRIME_TRANS', 'Prime de Transport', 'GAIN', '400', 'Indemnité de transport', True, 20),
            ('PRIME_RESP', 'Prime de Responsabilité', 'GAIN', 'salaire_base * 0.15', 'Prime pour les postes à responsabilité', True, 15),
            ('HEURES_SUP', 'Heures Supplémentaires', 'GAIN', '(salaire_base / 173.33) * 1.25', 'Heures supplémentaires majorées à 25%', True, 30),
            ('PRIME_ANCIEN', 'Prime d\'Ancienneté', 'GAIN', 'salaire_base * (anciennete_mois / 120) * 0.05', 'Prime basée sur l\'ancienneté', True, 25),
            
            # Retenues
            ('RET_RETARD', 'Retenue Retards', 'RETENUE', '(salaire_base / 26) * 0.5', 'Retenue pour retards répétés', True, 80),
            ('RET_ABSENCE', 'Retenue Absences', 'RETENUE', '(salaire_base / 26)', 'Retenue pour absences injustifiées', True, 85),
            ('AVANCE_SAL', 'Avance sur Salaire', 'RETENUE', '1000', 'Remboursement avance sur salaire', True, 90),
            ('RET_MATER', 'Retenue Matériel', 'RETENUE', '200', 'Retenue pour dégradation matériel', False, 95),
        ]
        
        self.rubriques = {}
        admin_user = None
        if 'admin' in self.employees:
            admin_user = self.employees['admin'].user
        
        for code, nom, type_rub, formule, description, actif, ordre in rubriques_data:
            rubrique, created = RubriquePersonnalisee.objects.get_or_create(
                code=code,
                defaults={
                    'nom': nom,
                    'type_rubrique': type_rub,
                    'mode_calcul': 'FORMULE',
                    'formule_personnalisee': formule,
                    'description': description,
                    'actif': actif,
                    'ordre_affichage': ordre,
                    'date_debut': datetime.now().date(),
                    'soumis_cnss': type_rub == 'GAIN',
                    'cree_par': admin_user
                }
            )
            self.rubriques[code] = rubrique
        
        self.stdout.write(f'📋 Rubriques créées: {len(self.rubriques)}')

    def assign_rubriques_to_employees(self):
        """Assigner des rubriques aux employés de manière réaliste"""
        
        # Tous les employés ont la prime de transport
        for emp in self.employees.values():
            EmployeRubrique.objects.get_or_create(
                employe=emp,
                rubrique=self.rubriques['PRIME_TRANS'],
                defaults={'montant_personnalise': Decimal('400'), 'date_debut': datetime.now().date(), 'actif': True}
            )
        
        # Prime de performance pour certains employés
        performance_employees = ['dev1', 'rh1', 'comm1', 'comptable1']
        for emp_key in performance_employees:
            if emp_key in self.employees:
                EmployeRubrique.objects.get_or_create(
                    employe=self.employees[emp_key],
                    rubrique=self.rubriques['PRIME_PERF'],
                    defaults={'date_debut': datetime.now().date(), 'actif': True}  # Calculé par formule
                )
        
        # Prime de responsabilité pour les managers
        resp_employees = ['drh', 'rh1', 'comm1', 'prod1']
        for emp_key in resp_employees:
            if emp_key in self.employees:
                EmployeRubrique.objects.get_or_create(
                    employe=self.employees[emp_key],
                    rubrique=self.rubriques['PRIME_RESP'],
                    defaults={'date_debut': datetime.now().date(), 'actif': True}
                )
        
        # Prime d'ancienneté pour les anciens employés
        ancien_employees = ['drh', 'dev1', 'comptable1', 'prod1']
        for emp_key in ancien_employees:
            if emp_key in self.employees:
                EmployeRubrique.objects.get_or_create(
                    employe=self.employees[emp_key],
                    rubrique=self.rubriques['PRIME_ANCIEN'],
                    defaults={'date_debut': datetime.now().date(), 'actif': True}
                )
        
        # Quelques retenues pour des cas spécifiques
        retenue_employees = [('prod2', 'RET_RETARD'), ('comm2', 'AVANCE_SAL')]
        for emp_key, ret_code in retenue_employees:
            if emp_key in self.employees and ret_code in self.rubriques:
                EmployeRubrique.objects.get_or_create(
                    employe=self.employees[emp_key],
                    rubrique=self.rubriques[ret_code],
                    defaults={'date_debut': datetime.now().date(), 'actif': True}
                )
        
        self.stdout.write(f'🔗 Rubriques assignées aux employés')

    def create_absences(self):
        """Créer quelques absences de test"""
        absence_data = [
            ('rh2', 'CONGE', 3, 'EN_ATTENTE'),
            ('dev2', 'MALADIE', 2, 'APPROUVE'),
            ('comm2', 'RTT', 1, 'APPROUVE'),
            ('prod2', 'CONGE', 5, 'REFUSE'),
        ]
        
        for emp_key, type_abs, nb_jours, statut in absence_data:
            if emp_key in self.employees:
                date_debut = datetime.now().date() + timedelta(days=random.randint(1, 30))
                Absence.objects.get_or_create(
                    employe=self.employees[emp_key],
                    type_absence=type_abs,
                    date_debut=date_debut,
                    defaults={
                        'date_fin': date_debut + timedelta(days=nb_jours-1),
                        'nombre_jours': nb_jours,
                        'statut': statut,
                        'motif': f'Demande de {type_abs.lower()}',
                    }
                )
        
        self.stdout.write(f'📅 Absences créées pour démonstration')
