#!/usr/bin/env python
"""
Script de diagnostic pour analyser le problème de la page accueil_moderne
qui s'affiche puis disparaît
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_paie.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from paie.models import Employe

def test_accueil_moderne():
    """Tester la page accueil_moderne et analyser les problèmes"""
    
    print("🔍 DIAGNOSTIC PAGE ACCUEIL_MODERNE")
    print("=" * 50)
    
    client = Client()
    User = get_user_model()
    
    # 1. Test sans connexion
    print("\n1. Test sans connexion:")
    response = client.get('/accueil_moderne/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirection vers: {response.url}")
    
    # 2. Test avec connexion admin
    print("\n2. Test avec utilisateur admin:")
    try:
        admin_user = User.objects.get(username='admin')
        client.force_login(admin_user)
        
        response = client.get('/accueil_moderne/')
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.get('Content-Type')}")
        print(f"   Taille du contenu: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Vérifier les éléments clés
            checks = [
                ('DOCTYPE html', 'DOCTYPE déclaré'),
                ('accueil_moderne.html', 'Template chargé'),
                ('loadSection', 'Fonction JavaScript loadSection'),
                ('DOMContentLoaded', 'Event listener DOM'),
                ('setTimeout', 'Délais JavaScript'),
                ('window.location', 'Gestion d\'URL'),
                ('/api/spa/', 'Appels API SPA'),
            ]
            
            print("\n   Vérifications du contenu:")
            for check, description in checks:
                found = check in content
                status = "✅" if found else "❌"
                print(f"   {status} {description}: {'Trouvé' if found else 'Manquant'}")
                
        # 3. Test des endpoints API SPA
        print("\n3. Test des endpoints API SPA:")
        api_endpoints = [
            '/api/spa/dashboard/',
            '/api/spa/dashboard-admin/',
            '/api/spa/dashboard-rh/',
            '/api/spa/employees/',
            '/api/spa/absences/',
            '/api/spa/payroll/',
            '/api/spa/reports/',
            '/api/spa/rubriques/',
        ]
        
        for endpoint in api_endpoints:
            try:
                response = client.get(endpoint)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} {endpoint}: {response.status_code}")
                if response.status_code != 200:
                    print(f"      Error: {response.content[:100]}")
            except Exception as e:
                print(f"   ❌ {endpoint}: Exception - {e}")
    
    except User.DoesNotExist:
        print("   ❌ Utilisateur admin non trouvé")
    
    # 4. Vérification des données
    print("\n4. Vérification des données:")
    employes_count = Employe.objects.filter(actif=True).count()
    print(f"   📊 Employés actifs: {employes_count}")
    
    # 5. Analyse des URLs
    print("\n5. Configuration des URLs:")
    try:
        url = reverse('paie:accueil_moderne')
        print(f"   ✅ URL accueil_moderne: {url}")
    except Exception as e:
        print(f"   ❌ Erreur URL: {e}")

def analyze_javascript_issues():
    """Analyser les problèmes JavaScript potentiels"""
    
    print("\n🔧 ANALYSE JAVASCRIPT")
    print("=" * 30)
    
    template_path = 'paie/templates/paie/accueil_moderne.html'
    
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Vérifications JavaScript
        js_issues = []
        
        # 1. Vérifier les setTimeout sans délai approprié
        import re
        setTimeout_matches = re.findall(r'setTimeout\([^,)]+,\s*(\d+)\)', content)
        short_delays = [int(delay) for delay in setTimeout_matches if int(delay) < 500]
        if short_delays:
            js_issues.append(f"⚠️ Délais setTimeout courts détectés: {short_delays}ms - Peut causer des problèmes de timing")
        
        # 2. Vérifier les redirections automatiques
        if 'window.location' in content and 'setTimeout' in content:
            js_issues.append("⚠️ Possible redirection automatique détectée")
        
        # 3. Vérifier les appels AJAX sans gestion d'erreur appropriée
        fetch_count = content.count('fetch(')
        catch_count = content.count('.catch(')
        if fetch_count > catch_count:
            js_issues.append(f"⚠️ {fetch_count - catch_count} appels fetch sans gestion d'erreur")
        
        if js_issues:
            print("   Problèmes détectés:")
            for issue in js_issues:
                print(f"   {issue}")
        else:
            print("   ✅ Aucun problème JavaScript évident détecté")
    else:
        print(f"   ❌ Template non trouvé: {template_path}")

def recommend_fixes():
    """Recommandations de correction"""
    
    print("\n💡 RECOMMANDATIONS")
    print("=" * 20)
    
    recommendations = [
        "1. Augmenter les délais setTimeout à minimum 500ms",
        "2. Ajouter des console.log pour tracer l'exécution",
        "3. Vérifier que tous les endpoints API fonctionnent",
        "4. Tester en mode DEBUG=False",
        "5. Vérifier les permissions utilisateur",
        "6. Ajouter une gestion d'erreur robuste aux appels AJAX",
        "7. Implémenter un système de fallback en cas d'échec"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")

if __name__ == "__main__":
    test_accueil_moderne()
    analyze_javascript_issues()
    recommend_fixes()
