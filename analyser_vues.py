#!/usr/bin/env python3
"""
Script de nettoyage des vues inutilisées dans PayrollPro
"""

import re

def analyser_vues_utilisees():
    """Analyser quelles vues sont réellement utilisées dans urls.py"""
    
    vues_utilisees = set()
    
    # Lire le fichier urls.py
    try:
        with open('paie/urls.py', 'r', encoding='utf-8') as f:
            contenu_urls = f.read()
            
        # Extraire toutes les vues utilisées
        patterns = [
            r"views\.(\w+)",
            r"views_\w+\.(\w+)",
            r"views_spa.*\.(\w+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, contenu_urls)
            vues_utilisees.update(matches)
            
    except FileNotFoundError:
        print("❌ Fichier urls.py non trouvé")
        return set()
    
    return vues_utilisees

def lister_toutes_vues():
    """Lister toutes les vues définies dans views.py"""
    
    vues_definies = set()
    
    try:
        with open('paie/views.py', 'r', encoding='utf-8') as f:
            contenu_views = f.read()
            
        # Extraire toutes les définitions de vues
        pattern = r"def (\w+)\(request"
        matches = re.findall(pattern, contenu_views)
        vues_definies.update(matches)
        
    except FileNotFoundError:
        print("❌ Fichier views.py non trouvé")
        return set()
    
    return vues_definies

def main():
    print("🧹 ANALYSE DES VUES INUTILISÉES")
    print("=" * 50)
    
    vues_utilisees = analyser_vues_utilisees()
    vues_definies = lister_toutes_vues()
    
    print(f"📊 Vues définies: {len(vues_definies)}")
    print(f"📊 Vues utilisées: {len(vues_utilisees)}")
    
    vues_inutilisees = vues_definies - vues_utilisees
    
    print(f"\n🗑️  VUES INUTILISÉES ({len(vues_inutilisees)}):")
    print("-" * 30)
    
    for vue in sorted(vues_inutilisees):
        print(f"  • {vue}")
    
    print(f"\n✅ VUES UTILISÉES ({len(vues_utilisees)}):")
    print("-" * 30)
    
    for vue in sorted(vues_utilisees):
        print(f"  • {vue}")
    
    # Identifier les vues potentiellement supprimables
    vues_anciennes = {
        'dashboard_admin', 'dashboard_rh', 'dashboard_employe',
        'liste_employes', 'calcul_paie', 'aide',
        'dashboard_admin_moderne', 'dashboard_rh_moderne'
    }
    
    vues_a_supprimer = vues_inutilisees & vues_anciennes
    
    print(f"\n🎯 VUES ANCIENNES À SUPPRIMER ({len(vues_a_supprimer)}):")
    print("-" * 40)
    
    for vue in sorted(vues_a_supprimer):
        print(f"  • {vue} (ancienne vue remplacée par SPA)")
    
    print(f"\n📝 RECOMMANDATIONS:")
    print("-" * 20)
    print("1. Supprimez les vues anciennes listées ci-dessus")
    print("2. Gardez les vues essentielles pour le SPA")
    print("3. Testez après suppression pour vérifier que tout fonctionne")
    
    return vues_a_supprimer

if __name__ == "__main__":
    vues_a_supprimer = main()
    
    print(f"\n🔧 PROCHAINES ÉTAPES:")
    print("1. Exécutez ce script pour voir les vues inutilisées")
    print("2. Supprimez manuellement les vues anciennes")
    print("3. Testez l'application après suppression")
