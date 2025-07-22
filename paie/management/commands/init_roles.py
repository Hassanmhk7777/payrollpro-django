# paie/management/commands/init_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from paie.models import Employe, Absence, BulletinPaie


class Command(BaseCommand):
    help = 'Initialise les groupes RH et Employe avec leurs permissions'

    def handle(self, *args, **options):
        # Créer les groupes
        group_rh, created = Group.objects.get_or_create(name='RH')
        group_employe, created = Group.objects.get_or_create(name='Employe')

        # Permissions pour le groupe RH
        rh_permissions = [
            # Employe
            'add_employe',
            'change_employe',
            'view_employe',
            # Absence
            'add_absence',
            'change_absence', 
            'view_absence',
            'delete_absence',
            # BulletinPaie
            'add_bulletinpaie',
            'change_bulletinpaie',
            'view_bulletinpaie',
        ]

        # Permissions pour le groupe Employe
        employe_permissions = [
            # Seulement vue limitée
            'view_absence',  # Ses propres absences
            'view_bulletinpaie',  # Ses propres bulletins
        ]

        # Assigner permissions RH
        for perm_name in rh_permissions:
            try:
                permission = Permission.objects.get(codename=perm_name)
                group_rh.permissions.add(permission)
                self.stdout.write(f"✅ Permission '{perm_name}' ajoutée au groupe RH")
            except Permission.DoesNotExist:
                self.stdout.write(f"⚠️ Permission '{perm_name}' non trouvée")

        # Assigner permissions Employe
        for perm_name in employe_permissions:
            try:
                permission = Permission.objects.get(codename=perm_name)
                group_employe.permissions.add(permission)
                self.stdout.write(f"✅ Permission '{perm_name}' ajoutée au groupe Employe")
            except Permission.DoesNotExist:
                self.stdout.write(f"⚠️ Permission '{perm_name}' non trouvée")

        self.stdout.write(
            self.style.SUCCESS('🎉 Groupes et permissions créés avec succès!')
        )