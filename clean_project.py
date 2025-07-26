#!/usr/bin/env python
"""
Script de nettoyage pour PayrollPro
Supprime les fichiers temporaires, cache et logs
"""

import os
import shutil
import glob
from pathlib import Path

def clean_project():
    """Nettoie le projet des fichiers temporaires"""
    project_root = Path(__file__).parent
    
    # Fichiers et dossiers à supprimer
    cleanup_patterns = [
        # Cache Python
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        
        # Logs
        "*.log",
        "logs/*.log",
        
        # Fichiers temporaires
        "*.tmp",
        "*.temp",
        "*~",
        "*.bak",
        
        # Fichiers de test temporaires
        "test_*.py",
        
        # Cache Django
        "staticfiles",
        
        # Fichiers de développement
        ".pytest_cache",
        ".coverage",
        "htmlcov",
    ]
    
    cleaned_files = 0
    cleaned_dirs = 0
    
    print("🧹 Nettoyage de PayrollPro en cours...")
    
    for pattern in cleanup_patterns:
        matches = list(project_root.glob(pattern))
        
        for match in matches:
            try:
                if match.is_file():
                    match.unlink()
                    cleaned_files += 1
                    print(f"  ✅ Supprimé fichier: {match.relative_to(project_root)}")
                elif match.is_dir():
                    shutil.rmtree(match)
                    cleaned_dirs += 1
                    print(f"  ✅ Supprimé dossier: {match.relative_to(project_root)}")
            except (OSError, PermissionError) as e:
                print(f"  ❌ Erreur lors de la suppression de {match}: {e}")
    
    print(f"\n🎉 Nettoyage terminé!")
    print(f"   📁 {cleaned_dirs} dossiers supprimés")
    print(f"   📄 {cleaned_files} fichiers supprimés")
    
    # Vérification de l'espace libéré
    print("\n📊 Structure finale:")
    essential_dirs = ["paie", "gestion_paie", "venv"]
    for dir_name in essential_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            print(f"   {dir_name}: {size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    clean_project()
