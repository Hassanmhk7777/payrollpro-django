#!/usr/bin/env python
"""
Script de diagnostic PayrollPro - Identification des problèmes de chargement SPA
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_paie.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from django.urls import reverse

def diagnostiquer_spa():
    """Diagnostiquer les problèmes SPA"""
    
    print("🔍 DIAGNOSTIC PAYROLLPRO - PROBLÈMES SPA")
    print("=" * 50)
    
    # Créer un client de test
    client = Client()
    
    # Créer ou récupérer un utilisateur de test
    try:
        user = User.objects.get(username='admin')
    except User.DoesNotExist:
        user = User.objects.create_user('testuser', 'test@test.com', 'testpass')
    
    # Se connecter
    client.force_login(user)
    
    # Test des URLs SPA
    urls_a_tester = [
        ('Dashboard', '/api/spa/dashboard/'),
        ('Calcul Paie', '/api/spa/payroll/'),
        ('Employés', '/api/spa/employees/'),
        ('Absences', '/api/spa/absences/'),
        ('Rapports', '/api/spa/reports/'),
        ('Rubriques', '/api/spa/rubriques/'),
    ]
    
    print("🌐 Test des endpoints SPA:")
    for nom, url in urls_a_tester:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"  ✅ {nom}: OK (200)")
                
                # Vérifier le contenu JSON
                if hasattr(response, 'json'):
                    try:
                        data = response.json()
                        if data.get('success'):
                            print(f"     📋 Contenu: Valide")
                        else:
                            print(f"     ❌ Contenu: {data.get('error', 'Erreur inconnue')}")
                    except:
                        print(f"     ⚠️ Contenu: Pas JSON valide")
                        
            else:
                print(f"  ❌ {nom}: Erreur {response.status_code}")
                
        except Exception as e:
            print(f"  🚫 {nom}: Exception - {str(e)}")
    
    print("\n🗂️ Test des modèles:")
    try:
        from paie.models import Employe, Site, Departement, RubriquePersonnalisee
        
        employes_count = Employe.objects.count()
        sites_count = Site.objects.count()
        dept_count = Departement.objects.count()
        rub_count = RubriquePersonnalisee.objects.count()
        
        print(f"  📊 Employés: {employes_count}")
        print(f"  🏢 Sites: {sites_count}")
        print(f"  🏛️ Départements: {dept_count}")
        print(f"  📋 Rubriques: {rub_count}")
        
        if employes_count == 0:
            print("  ⚠️ Aucun employé - Exécuter create_demo_data")
            
    except Exception as e:
        print(f"  ❌ Erreur modèles: {e}")
    
    print("\n🔧 Test des imports:")
    try:
        from paie.views_spa_fixed import spa_dashboard_fixed, spa_payroll_fixed
        print("  ✅ views_spa_fixed: OK")
    except Exception as e:
        print(f"  ❌ views_spa_fixed: {e}")
    
    try:
        from paie.views_rubriques_complete import rubriques_spa_view
        print("  ✅ views_rubriques_complete: OK")
    except Exception as e:
        print(f"  ❌ views_rubriques_complete: {e}")
    
    print("\n📝 Recommandations:")
    if employes_count == 0:
        print("  1. Exécuter: python manage.py shell -c \"from paie.management.commands.create_demo_data_complete import Command; Command().handle()\"")
    
    print("  2. Vérifier les logs Django pour erreurs détaillées")
    print("  3. S'assurer que l'utilisateur a les bonnes permissions")
    print("  4. Tester en mode DEBUG=True")

if __name__ == "__main__":
    diagnostiquer_spa()
