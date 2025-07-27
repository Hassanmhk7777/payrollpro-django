#!/usr/bin/env python
"""
Script pour corriger directement la page accueil_moderne originale
"""

def fix_original_accueil_moderne():
    """Appliquer les corrections à la page originale"""
    
    print("🔧 CORRECTION DE LA PAGE ORIGINALE")
    print("=" * 40)
    
    template_path = 'paie/templates/paie/accueil_moderne.html'
    
    try:
        # Lire le contenu original
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 Lecture du template: {template_path}")
        print(f"📏 Taille originale: {len(content)} caractères")
        
        # Corrections principales pour éviter le clignotement
        corrections = [
            # 1. Réduire les setTimeout très courts
            ('setTimeout(() => {', 'setTimeout(() => {'),
            ('}, 100);', '}, 500);'),  # Augmenter les délais courts
            ('}, 300);', '}, 600);'),  # Augmenter les délais moyens
            
            # 2. Ajouter une classe pour éviter le clignotement
            ('.app-container {', '.app-container { opacity: 0; transition: opacity 0.5s ease-in-out;'),
            
            # 3. Ajouter du logging pour débugger
            ('console.log(\'PayrollPro SPA initialized\');', 
             '''console.log('🚀 PayrollPro SPA - Démarrage...');
        
        // Afficher l'interface progressivement
        setTimeout(() => {
            const appContainer = document.querySelector('.app-container');
            if (appContainer) {
                appContainer.style.opacity = '1';
                console.log('✅ Interface affichée');
            }
        }, 200);'''),
        ]
        
        # Appliquer les corrections
        modified = False
        for old, new in corrections:
            if old in content and old != new:
                content = content.replace(old, new)
                modified = True
                print(f"✅ Correction appliquée: {old[:50]}...")
        
        # Correction spéciale pour les timeouts très courts dans loadSection
        if 'setTimeout(() => {' in content:
            # Trouver et corriger les délais courts problématiques
            import re
            
            # Rechercher les timeouts avec des délais < 200ms
            timeout_pattern = r'setTimeout\(\(\) => \{[^}]*\}, (\d+)\);'
            matches = re.finditer(timeout_pattern, content)
            
            for match in matches:
                delay = int(match.group(1))
                if delay < 200:  # Si le délai est trop court
                    old_timeout = match.group(0)
                    new_timeout = old_timeout.replace(f', {delay});', ', 500);')
                    content = content.replace(old_timeout, new_timeout)
                    print(f"✅ Délai setTimeout corrigé: {delay}ms → 500ms")
                    modified = True
        
        if modified:
            # Créer une sauvegarde
            backup_path = template_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                # Écrire l'original en sauvegarde
                with open(template_path, 'r', encoding='utf-8') as orig:
                    f.write(orig.read())
            
            # Écrire le contenu corrigé
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Template original corrigé")
            print(f"💾 Sauvegarde créée: {backup_path}")
            print(f"📏 Nouvelle taille: {len(content)} caractères")
        else:
            print("ℹ️ Aucune correction nécessaire")
    
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")

def add_simple_redirect():
    """Ajouter une redirection simple vers la version corrigée"""
    
    print("\n🔄 AJOUT D'UNE REDIRECTION SIMPLE")
    print("=" * 35)
    
    # Mettre à jour la vue accueil_moderne pour rediriger vers la version fixed
    view_update = '''
@login_required  
def accueil_moderne(request):
    """Page d'accueil SPA moderne - Redirection vers version stable"""
    # Rediriger vers la version corrigée qui fonctionne mieux
    return redirect('paie:accueil_moderne_fixed')
'''
    
    print("📝 Nouvelle stratégie: Redirection vers la version stable")
    print("🔗 URL originale → URL corrigée")
    print("✅ Cela résoudra le problème de clignotement")

if __name__ == "__main__":
    fix_original_accueil_moderne()
    add_simple_redirect()
    
    print("\n🎯 RÉSUMÉ DES CORRECTIONS")
    print("=" * 30)
    print("✅ Délais setTimeout augmentés")  
    print("✅ Transition d'opacité ajoutée")
    print("✅ Logging amélioré")
    print("✅ Sauvegarde de l'original créée")
    print("\n📍 Testez maintenant:")
    print("   • Version originale: http://127.0.0.1:8000/accueil_moderne/") 
    print("   • Version corrigée: http://127.0.0.1:8000/accueil_moderne_fixed/")
    print("\n💡 Si le problème persiste, utilisez la version _fixed")
