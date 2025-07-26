from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from paie.models import Employe, Site, Departement, Absence
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Créer des données de démonstration pour l\'application PayrollPro'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Création des données de démonstration...'))

        # Créer des sites
        site1, created = Site.objects.get_or_create(
            code='CAS',
            defaults={
                'nom': 'Siège Social Casablanca',
                'raison_sociale': 'PayrollPro SARL',
                'adresse': 'Boulevard Mohammed V, Casablanca',
                'ville': 'Casablanca',
                'actif': True
            }
        )
        
        site2, created = Site.objects.get_or_create(
            code='RAB',
            defaults={
                'nom': 'Filiale Rabat',
                'raison_sociale': 'PayrollPro SARL - Filiale Rabat',
                'adresse': 'Avenue Hassan II, Rabat',
                'ville': 'Rabat',
                'actif': True
            }
        )

        # Créer des départements
        dept_rh, created = Departement.objects.get_or_create(
            code='RH',
            site=site1,
            defaults={'nom': 'Ressources Humaines', 'actif': True}
        )
        
        dept_it, created = Departement.objects.get_or_create(
            code='IT',
            site=site1,
            defaults={'nom': 'Informatique', 'actif': True}
        )
        
        dept_compta, created = Departement.objects.get_or_create(
            code='COMPTA',
            site=site1,
            defaults={'nom': 'Comptabilité', 'actif': True}
        )

        # Créer des employés de démonstration
        employes_data = [
            {
                'nom': 'Benali',
                'prenom': 'Ahmed',
                'fonction': 'Développeur Senior',
                'salaire_base': 12000,
                'site': site1,
                'departement': dept_it
            },
            {
                'nom': 'El Mansouri',
                'prenom': 'Fatima',
                'fonction': 'Responsable RH',
                'salaire_base': 15000,
                'site': site1,
                'departement': dept_rh
            },
            {
                'nom': 'Tazi',
                'prenom': 'Youssef',
                'fonction': 'Comptable',
                'salaire_base': 9500,
                'site': site1,
                'departement': dept_compta
            },
            {
                'nom': 'Alami',
                'prenom': 'Khadija',
                'fonction': 'Développeur Junior',
                'salaire_base': 8000,
                'site': site1,
                'departement': dept_it
            },
            {
                'nom': 'Benjelloun',
                'prenom': 'Omar',
                'fonction': 'Analyste Financier',
                'salaire_base': 11000,
                'site': site1,
                'departement': dept_compta
            },
            {
                'nom': 'Chraibi',
                'prenom': 'Samira',
                'fonction': 'Chef de Projet',
                'salaire_base': 13500,
                'site': site2,
                'departement': dept_it
            },
            {
                'nom': 'Ouali',
                'prenom': 'Hassan',
                'fonction': 'Assistant RH',
                'salaire_base': 7500,
                'site': site2,
                'departement': dept_rh
            },
            {
                'nom': 'Benyahia',
                'prenom': 'Laila',
                'fonction': 'Administrateur Système',
                'salaire_base': 10500,
                'site': site1,
                'departement': dept_it
            }
        ]

        employes = []
        for i, emp_data in enumerate(employes_data, 1):
            # Générer un matricule et CIN unique
            matricule = f"EMP{i:03d}"
            cin = f"AB{100000 + i}"
            
            employe, created = Employe.objects.get_or_create(
                matricule=matricule,
                defaults={
                    'nom': emp_data['nom'],
                    'prenom': emp_data['prenom'],
                    'cin': cin,
                    'fonction': emp_data['fonction'],
                    'salaire_base': emp_data['salaire_base'],
                    'site': emp_data['site'],
                    'departement': emp_data['departement'],
                    'date_embauche': datetime.now().date() - timedelta(days=365),
                    'actif': True
                }
            )
            employes.append(employe)
            if created:
                self.stdout.write(f'✓ Employé créé: {employe.nom} {employe.prenom}')

        # Créer des absences de démonstration
        absences_data = [
            {
                'employe': employes[0],  # Ahmed Benali
                'type_absence': 'CONGE',
                'date_debut': datetime.now().date() + timedelta(days=10),
                'date_fin': datetime.now().date() + timedelta(days=14),
                'statut': 'EN_ATTENTE'
            },
            {
                'employe': employes[1],  # Fatima El Mansouri
                'type_absence': 'MALADIE',
                'date_debut': datetime.now().date() - timedelta(days=5),
                'date_fin': datetime.now().date() - timedelta(days=3),
                'statut': 'APPROUVE'
            },
            {
                'employe': employes[2],  # Youssef Tazi
                'type_absence': 'RTT',
                'date_debut': datetime.now().date() + timedelta(days=20),
                'date_fin': datetime.now().date() + timedelta(days=22),
                'statut': 'EN_ATTENTE'
            },
            {
                'employe': employes[3],  # Khadija Alami
                'type_absence': 'SANS_SOLDE',
                'date_debut': datetime.now().date() + timedelta(days=5),
                'date_fin': datetime.now().date() + timedelta(days=5),
                'statut': 'REFUSE'
            },
            {
                'employe': employes[4],  # Omar Benjelloun
                'type_absence': 'CONGE',
                'date_debut': datetime.now().date() + timedelta(days=30),
                'date_fin': datetime.now().date() + timedelta(days=39),
                'statut': 'EN_ATTENTE'
            }
        ]

        for abs_data in absences_data:
            duree = (abs_data['date_fin'] - abs_data['date_debut']).days + 1
            absence, created = Absence.objects.get_or_create(
                employe=abs_data['employe'],
                date_debut=abs_data['date_debut'],
                defaults={
                    'type_absence': abs_data['type_absence'],
                    'date_fin': abs_data['date_fin'],
                    'nombre_jours': duree,
                    'statut': abs_data['statut'],
                    'motif': f"Demande de {abs_data['type_absence'].lower()}"
                }
            )
            if created:
                self.stdout.write(f'✓ Absence créée: {absence.employe.nom} - {absence.type_absence}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Données de démonstration créées avec succès!\n'
                f'📊 {len(employes)} employés créés\n'
                f'📅 {len(absences_data)} absences créées\n'
                f'🏢 {Site.objects.count()} sites créés\n'
                f'🏛️ {Departement.objects.count()} départements créés\n'
            )
        )
