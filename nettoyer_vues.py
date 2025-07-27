#!/usr/bin/env python3
"""
Nettoyage des vues inutilisées et problématiques dans PayrollPro
"""

import os
import re

def corriger_vue_dashboard_admin():
    """Corriger la vue dashboard_admin qui est malformée"""
    print("🔧 Correction de la vue dashboard_admin...")
    
    try:
        with open('paie/views.py', 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        # Trouver et corriger la vue dashboard_admin
        pattern = r'@login_required\ndef dashboard_admin\(request\):\s*"""Dashboard pour les administrateurs - Redirection vers SPA moderne"""\s*return redirect\(\'paie:accueil_moderne\'\)\s*.*?(?=@|\ndef |\Z)'
        
        nouvelle_vue = '''@login_required
def dashboard_admin(request):
    """Dashboard pour les administrateurs - Redirection vers SPA moderne"""
    return redirect('paie:accueil_moderne')

'''
        
        contenu_corrige = re.sub(pattern, nouvelle_vue, contenu, flags=re.DOTALL)
        
        with open('paie/views.py', 'w', encoding='utf-8') as f:
            f.write(contenu_corrige)
        
        print("✅ Vue dashboard_admin corrigée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def supprimer_vues_inutilisees():
    """Supprimer les vues qui ne sont vraiment plus utilisées"""
    
    vues_a_supprimer = [
        'ajouter_rubrique_ponctuelle',
        'assignation_massive_rubriques', 
        'calendrier_absences',
        'connexion_personnalisee',
        'dashboard_rubriques_admin',
        'generer_bulletin_pdf',
        'gestion_rubriques_employe',
        'modifier_assignation_rubrique',
        'page_aide',
        'statistiques_absences',
        'supprimer_assignation_rubrique',
        'test_calcul_absences',
        'validation_lot_absences',
        'valider_absence'
    ]
    
    print(f"🗑️  Suppression de {len(vues_a_supprimer)} vues inutilisées...")
    
    try:
        with open('paie/views.py', 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        lignes_supprimees = 0
        
        for vue in vues_a_supprimer:
            # Pattern pour trouver la définition complète de la vue
            pattern = rf'(@[\w_.]+\s*)*def {vue}\([^)]*\):.*?(?=(@[\w_.]+\s*)*def \w+\(|class \w+|$)'
            
            matches = re.findall(pattern, contenu, flags=re.DOTALL)
            if matches:
                contenu = re.sub(pattern, '', contenu, flags=re.DOTALL)
                lignes_supprimees += len(matches[0].split('\n')) if matches else 0
                print(f"  ✅ Vue {vue} supprimée")
            else:
                print(f"  ⚠️  Vue {vue} non trouvée")
        
        # Nettoyer les lignes vides multiples
        contenu = re.sub(r'\n{3,}', '\n\n', contenu)
        
        with open('paie/views.py', 'w', encoding='utf-8') as f:
            f.write(contenu)
        
        print(f"✅ {lignes_supprimees} lignes supprimées au total")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        return False

def nettoyer_imports():
    """Nettoyer les imports inutilisés"""
    print("🧹 Nettoyage des imports...")
    
    try:
        with open('paie/views.py', 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        # Supprimer les imports dupliqués ou inutilisés
        lignes = contenu.split('\n')
        imports_vus = set()
        lignes_nettoyees = []
        
        for ligne in lignes:
            if ligne.strip().startswith('from ') or ligne.strip().startswith('import '):
                if ligne not in imports_vus:
                    imports_vus.add(ligne)
                    lignes_nettoyees.append(ligne)
            else:
                lignes_nettoyees.append(ligne)
        
        contenu_nettoye = '\n'.join(lignes_nettoyees)
        
        with open('paie/views.py', 'w', encoding='utf-8') as f:
            f.write(contenu_nettoye)
        
        print("✅ Imports nettoyés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage des imports: {e}")
        return False

def verifier_syntaxe():
    """Vérifier que le fichier Python est syntaxiquement correct"""
    print("🔍 Vérification de la syntaxe...")
    
    try:
        import ast
        with open('paie/views.py', 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        ast.parse(contenu)
        print("✅ Syntaxe Python correcte")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    print("🧹 NETTOYAGE DES VUES PAYROLLPRO")
    print("=" * 50)
    
    # Sauvegarde avant modification
    print("💾 Création d'une sauvegarde...")
    try:
        import shutil
        shutil.copy2('paie/views.py', 'paie/views_backup.py')
        print("✅ Sauvegarde créée: paie/views_backup.py")
    except Exception as e:
        print(f"⚠️  Impossible de créer la sauvegarde: {e}")
    
    # Étapes de nettoyage
    etapes = [
        ("Correction dashboard_admin", corriger_vue_dashboard_admin),
        ("Suppression vues inutilisées", supprimer_vues_inutilisees),
        ("Nettoyage imports", nettoyer_imports),
        ("Vérification syntaxe", verifier_syntaxe)
    ]
    
    resultats = {}
    for nom, fonction in etapes:
        print(f"\n📋 {nom}...")
        resultats[nom] = fonction()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU NETTOYAGE")
    print("=" * 50)
    
    succes = 0
    for nom, resultat in resultats.items():
        status = "✅ RÉUSSI" if resultat else "❌ ÉCHOUÉ"
        print(f"{nom:.<30} {status}")
        if resultat:
            succes += 1
    
    print(f"\n🎯 RÉSULTAT: {succes}/{len(resultats)} étapes réussies")
    
    if succes == len(resultats):
        print("🎉 Nettoyage terminé avec succès!")
        print("📝 Testez maintenant l'application pour vérifier que tout fonctionne")
    else:
        print("⚠️  Certaines étapes ont échoué")
        print("💡 Vous pouvez restaurer depuis paie/views_backup.py si nécessaire")

if __name__ == "__main__":
    main()
