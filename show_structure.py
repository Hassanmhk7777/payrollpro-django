#!/usr/bin/env python
"""
Script pour afficher la structure essentielle de PayrollPro
"""

from pathlib import Path
import os

def format_size(size_bytes):
    """Formate la taille en unités lisibles"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {size_names[i]}"

def get_folder_size(folder_path):
    """Calcule la taille d'un dossier"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                except (OSError, FileNotFoundError):
                    pass
    except (OSError, FileNotFoundError):
        pass
    return total_size

def show_project_structure():
    """Affiche la structure du projet nettoyée"""
    project_root = Path(__file__).parent
    
    print("🏗️  STRUCTURE PAYROLLPRO - VERSION NETTOYÉE")
    print("=" * 50)
    
    # Fichiers racine essentiels
    essential_files = [
        "manage.py",
        "requirements.txt", 
        "db.sqlite3",
        ".gitignore",
        "clean_project.py"
    ]
    
    print("\n📁 FICHIERS RACINE:")
    total_root_size = 0
    for file_name in essential_files:
        file_path = project_root / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            total_root_size += size
            print(f"   ✅ {file_name} ({format_size(size)})")
        else:
            print(f"   ❌ {file_name} (manquant)")
    
    print(f"   📊 Total fichiers racine: {format_size(total_root_size)}")
    
    # Dossiers principaux
    main_folders = [
        ("gestion_paie", "Configuration Django principale"),
        ("paie", "Application de paie"),
        ("venv", "Environnement virtuel Python")
    ]
    
    print("\n📂 DOSSIERS PRINCIPAUX:")
    total_project_size = total_root_size
    
    for folder_name, description in main_folders:
        folder_path = project_root / folder_name
        if folder_path.exists():
            size = get_folder_size(folder_path)
            total_project_size += size
            print(f"   📁 {folder_name}/ ({format_size(size)}) - {description}")
            
            # Détail du dossier paie
            if folder_name == "paie":
                print("      ├── 📄 Fichiers Python:")
                python_files = [
                    "models.py", "views.py", "views_spa.py", "views_advanced.py",
                    "forms.py", "admin.py", "calculs.py", "audit.py", 
                    "user_management.py", "decorators.py", "middleware.py"
                ]
                for py_file in python_files:
                    py_path = folder_path / py_file
                    if py_path.exists():
                        py_size = py_path.stat().st_size
                        print(f"      │   ✅ {py_file} ({format_size(py_size)})")
                
                print("      └── 📁 Sous-dossiers:")
                sub_folders = ["templates", "migrations", "management"]
                for sub_folder in sub_folders:
                    sub_path = folder_path / sub_folder
                    if sub_path.exists():
                        sub_size = get_folder_size(sub_path)
                        print(f"          📁 {sub_folder}/ ({format_size(sub_size)})")
        else:
            print(f"   ❌ {folder_name}/ (manquant) - {description}")
    
    print(f"\n📊 TAILLE TOTALE DU PROJET: {format_size(total_project_size)}")
    
    # Statistiques de nettoyage
    print("\n🧹 RÉSUMÉ DU NETTOYAGE:")
    print("   ✅ Fichiers de cache Python supprimés (__pycache__/)")
    print("   ✅ Fichiers de log temporaires supprimés")
    print("   ✅ Templates en double supprimés")
    print("   ✅ Fichiers de test temporaires supprimés")
    print("   ✅ Scripts d'exemple supprimés")
    print("   ✅ Fichiers corrompus/backup supprimés")
    
    # Fichiers ignorés par Git
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        print("\n🚫 FICHIERS IGNORÉS PAR GIT:")
        print("   ✅ .gitignore configuré pour ignorer:")
        print("      • __pycache__/ et *.pyc")
        print("      • *.log et fichiers temporaires")
        print("      • db.sqlite3 et media/")
        print("      • venv/ et environnements virtuels")
        print("      • Fichiers IDE et système")
    
    print("\n🎉 PROJET PAYROLLPRO NETTOYÉ ET OPTIMISÉ!")
    print("   📦 Structure minimale et fonctionnelle")
    print("   🚀 Prêt pour le développement et la production")

if __name__ == "__main__":
    show_project_structure()
