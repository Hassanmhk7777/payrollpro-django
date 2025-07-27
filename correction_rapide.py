#!/usr/bin/env python
"""
Script de correction rapide PayrollPro
Résout les problèmes de chargement SPA et initialise les données
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_paie.settings')
django.setup()

from django.contrib.auth.models import User, Group
from paie.models import Employe, Site, Departement

def correction_rapide():
    """Appliquer les corrections rapides"""
    
    print("🔧 CORRECTION RAPIDE PAYROLLPRO")
    print("=" * 40)
    
    # 1. Créer les groupes d'utilisateurs
    print("👥 Création des groupes...")
    for group_name in ['Admin', 'RH', 'Employe']:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"  ✅ Groupe {group_name} créé")
        else:
            print(f"  ✓ Groupe {group_name} existe déjà")
    
    # 2. Vérifier/créer un utilisateur admin
    print("\n🔑 Vérification utilisateur admin...")
    try:
        admin_user = User.objects.get(username='admin')
        print("  ✓ Utilisateur admin existe")
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@payrollpro.ma',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        admin_group = Group.objects.get(name='Admin')
        admin_user.groups.add(admin_group)
        print("  ✅ Utilisateur admin créé (admin/admin123)")
    
    # 3. Vérifier les données de base
    print("\n📊 Vérification données de base...")
    employes_count = Employe.objects.count()
    sites_count = Site.objects.count()
    dept_count = Departement.objects.count()
    
    print(f"  📈 Employés: {employes_count}")
    print(f"  🏢 Sites: {sites_count}")
    print(f"  🏛️ Départements: {dept_count}")
    
    if employes_count == 0:
        print("\n🚀 Création des données de démonstration...")
        try:
            from paie.management.commands.create_demo_data_complete import Command
            cmd = Command()
            cmd.handle()
            print("  ✅ Données de démonstration créées")
        except Exception as e:
            print(f"  ❌ Erreur création données: {e}")
            # Utiliser l'ancienne commande si la nouvelle échoue
            try:
                from paie.management.commands.create_demo_data import Command
                cmd = Command()
                cmd.handle()
                print("  ✅ Données de base créées")
            except Exception as e2:
                print(f"  ❌ Erreur données de base: {e2}")
    
    # 4. Test des vues SPA
    print("\n🌐 Test des vues SPA...")
    try:
        from paie.views_spa_fixed import spa_dashboard_fixed, spa_payroll_fixed
        print("  ✅ Vues SPA corrigées importées")
    except Exception as e:
        print(f"  ❌ Erreur import vues SPA: {e}")
    
    try:
        from paie.views_rubriques_complete import rubriques_spa_view
        print("  ✅ Vues rubriques importées")
    except Exception as e:
        print(f"  ❌ Erreur import vues rubriques: {e}")
    
    print("\n✅ CORRECTION TERMINÉE")
    print("=" * 40)
    print("🌐 Vous pouvez maintenant tester:")
    print("  1. Se connecter avec: admin / admin123")
    print("  2. Naviguer dans l'interface SPA")
    print("  3. Tester le module Calcul de Paie")
    print("  4. Vérifier les rubriques personnalisées")
    
    return True

if __name__ == "__main__":
    correction_rapide()
