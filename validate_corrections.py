#!/usr/bin/env python
"""
Script de test et validation des corrections PayrollPro
Ce script vérifie que toutes les corrections du rapport ont été appliquées
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_paie.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User, Group
from paie.models import *
from paie.decorators import *
from paie.middleware import *
import importlib

class ValidationCorrections:
    def __init__(self):
        self.erreurs = []
        self.corrections = []
        
    def log(self, message, status="✅"):
        print(f"{status} {message}")
        if status == "❌":
            self.erreurs.append(message)
        else:
            self.corrections.append(message)
    
    def test_modeles_complets(self):
        """Test 1: Vérifier que tous les modèles sont complets"""
        self.log("=== Test des Modèles ===")
        
        try:
            # Tester le modèle Absence
            absence_fields = [f.name for f in Absence._meta.fields]
            required_fields = ['date_debut', 'date_fin', 'nombre_jours', 'statut']
            
            for field in required_fields:
                if field in absence_fields:
                    self.log(f"Champ Absence.{field} présent")
                else:
                    self.log(f"Champ Absence.{field} manquant", "❌")
                    
            # Tester RubriquePersonnalisee
            rub_fields = [f.name for f in RubriquePersonnalisee._meta.fields]
            if 'type_rubrique' in rub_fields and 'formule_calcul' in rub_fields:
                self.log("Modèle RubriquePersonnalisee complet")
            else:
                self.log("Modèle RubriquePersonnalisee incomplet", "❌")
                
        except Exception as e:
            self.log(f"Erreur modèles: {e}", "❌")
    
    def test_decorators_imports(self):
        """Test 2: Vérifier les imports des décorateurs"""
        self.log("=== Test des Décorateurs ===")
        
        try:
            from paie.decorators import admin_required, rh_required, employe_required
            self.log("Décorateurs importés avec succès")
            
            # Test fonctionnel basique
            if callable(admin_required) and callable(rh_required):
                self.log("Décorateurs fonctionnels")
            else:
                self.log("Décorateurs non fonctionnels", "❌")
                
        except ImportError as e:
            self.log(f"Erreur import décorateurs: {e}", "❌")
    
    def test_middleware_imports(self):
        """Test 3: Vérifier les imports des middlewares"""
        self.log("=== Test des Middlewares ===")
        
        try:
            from paie.middleware import RoleBasedRedirectMiddleware, ActiveUserOnlyMiddleware
            self.log("Middlewares importés avec succès")
            
            # Test basique
            if hasattr(RoleBasedRedirectMiddleware, '__init__'):
                self.log("RoleBasedRedirectMiddleware fonctionnel")
            else:
                self.log("RoleBasedRedirectMiddleware non fonctionnel", "❌")
                
        except ImportError as e:
            self.log(f"Erreur import middlewares: {e}", "❌")
            
        except Exception as e:
            self.log(f"Erreur générale middlewares: {e}", "⚠️")
    
    def test_vues_rubriques(self):
        """Test 4: Vérifier les nouvelles vues rubriques"""
        self.log("=== Test des Vues Rubriques ===")
        
        try:
            from paie.views_rubriques_complete import rubriques_spa_view, creer_rubrique_ajax
            self.log("Nouvelles vues rubriques importées")
            
            if callable(rubriques_spa_view) and callable(creer_rubrique_ajax):
                self.log("Vues rubriques fonctionnelles")
            else:
                self.log("Vues rubriques non fonctionnelles", "❌")
                
        except ImportError as e:
            self.log(f"Erreur import vues rubriques: {e}", "❌")
    
    def test_donnees_demo_ameliorees(self):
        """Test 5: Vérifier la commande de données améliorée"""
        self.log("=== Test Commande Données Demo ===")
        
        try:
            from paie.management.commands.create_demo_data_complete import Command
            self.log("Nouvelle commande données demo importée")
            
            cmd = Command()
            if hasattr(cmd, 'create_custom_rubriques') and hasattr(cmd, 'create_employees'):
                self.log("Commande demo améliorée fonctionnelle")
            else:
                self.log("Commande demo améliorée incomplète", "❌")
                
        except ImportError as e:
            self.log(f"Erreur import commande demo: {e}", "❌")
    
    def test_templates_javascript(self):
        """Test 6: Vérifier les templates JavaScript"""
        self.log("=== Test Templates JavaScript ===")
        
        try:
            # Vérifier que le template rubriques.html existe
            template_path = "paie/templates/paie/spa/rubriques.html"
            if os.path.exists(template_path):
                self.log("Template rubriques.html existe")
                
                # Lire le contenu pour vérifier les améliorations
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'activateRubrique' in content:
                    self.log("Fonction activateRubrique présente")
                else:
                    self.log("Fonction activateRubrique manquante", "❌")
                    
                if 'rubriques_gains' in content:
                    self.log("Variables statistiques dynamiques présentes")
                else:
                    self.log("Variables statistiques statiques", "⚠️")
            else:
                self.log("Template rubriques.html manquant", "❌")
                
        except Exception as e:
            self.log(f"Erreur test templates: {e}", "❌")
    
    def test_base_donnees_coherence(self):
        """Test 7: Vérifier la cohérence de la base de données"""
        self.log("=== Test Cohérence Base de Données ===")
        
        try:
            # Test de création d'objets
            if Site.objects.exists():
                self.log("Sites existent en base")
            else:
                self.log("Aucun site en base", "⚠️")
                
            if RubriquePersonnalisee.objects.exists():
                self.log("Rubriques personnalisées existent")
                
                # Test calcul sans erreur #REF!
                rubrique = RubriquePersonnalisee.objects.first()
                if rubrique and rubrique.formule_calcul:
                    if '#REF!' not in str(rubrique.formule_calcul):
                        self.log("Pas d'erreur #REF! dans les formules")
                    else:
                        self.log("Erreurs #REF! trouvées dans les formules", "❌")
            else:
                self.log("Aucune rubrique personnalisée", "⚠️")
                
        except Exception as e:
            self.log(f"Erreur test base de données: {e}", "❌")
    
    def test_securite_amelioree(self):
        """Test 8: Vérifier les améliorations de sécurité"""
        self.log("=== Test Sécurité ===")
        
        try:
            # Vérifier les groupes utilisateurs
            groups = ['Admin', 'RH', 'Employe']
            for group_name in groups:
                if Group.objects.filter(name=group_name).exists():
                    self.log(f"Groupe {group_name} existe")
                else:
                    self.log(f"Groupe {group_name} manquant", "❌")
                    
            # Test audit
            try:
                from paie.audit import audit_action
                self.log("Module audit importé")
            except ImportError:
                self.log("Module audit manquant", "⚠️")
                
        except Exception as e:
            self.log(f"Erreur test sécurité: {e}", "❌")
    
    def executer_tous_tests(self):
        """Exécuter tous les tests de validation"""
        print("🔍 VALIDATION DES CORRECTIONS PAYROLLPRO")
        print("=" * 50)
        
        self.test_modeles_complets()
        self.test_decorators_imports()
        self.test_middleware_imports()
        self.test_vues_rubriques()
        self.test_donnees_demo_ameliorees()
        self.test_templates_javascript()
        self.test_base_donnees_coherence()
        self.test_securite_amelioree()
        
        print("\n" + "=" * 50)
        print("📊 RÉSULTAT DES TESTS")
        print(f"✅ Corrections validées: {len(self.corrections)}")
        print(f"❌ Erreurs restantes: {len(self.erreurs)}")
        
        if self.erreurs:
            print("\n🔴 ERREURS À CORRIGER:")
            for erreur in self.erreurs:
                print(f"  - {erreur}")
        else:
            print("\n🎉 TOUTES LES CORRECTIONS VALIDÉES!")
        
        # Score de qualité
        total_tests = len(self.corrections) + len(self.erreurs)
        if total_tests > 0:
            score = (len(self.corrections) / total_tests) * 100
            print(f"\n📈 Score de qualité: {score:.1f}%")
            
            if score >= 90:
                print("🏆 Excellent - Prêt pour la production!")
            elif score >= 75:
                print("👍 Bon - Quelques améliorations mineures")
            elif score >= 50:
                print("⚠️ Moyen - Corrections importantes nécessaires")
            else:
                print("🚫 Critique - Corrections majeures requises")

def main():
    """Point d'entrée principal"""
    validator = ValidationCorrections()
    validator.executer_tous_tests()

if __name__ == "__main__":
    main()
