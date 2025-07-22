# Generated manually - Ajout des champs user et role_systeme
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('paie', '0001_initial'),  # Remplacez par votre dernière migration
    ]

    operations = [
        migrations.AddField(
            model_name='employe',
            name='user',
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                help_text="Compte utilisateur pour l'accès au système"
            ),
        ),
        migrations.AddField(
            model_name='employe',
            name='role_systeme',
            field=models.CharField(
                choices=[('EMPLOYE', 'Employé'), ('RH', 'Ressources Humaines')],
                default='EMPLOYE',
                help_text='Rôle dans le système de paie',
                max_length=20
            ),
        ),
    ]