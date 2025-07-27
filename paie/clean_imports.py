"""
Script de nettoyage des imports dans views.py
À exécuter pour corriger les imports dupliqués
"""

def nettoyer_imports_views():
    imports_corriges = """# Imports Django - Version corrigée
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Avg, Q
from django.db import models, transaction
from django.utils import timezone
from datetime import datetime, date
import json
from decimal import Decimal

# Imports locaux
from .models import Employe, RubriquePersonnalisee, EmployeRubrique, BulletinPaie, ParametrePaie, ElementPaie, Absence, Site, Departement
from .forms import RubriqueRapideForm, AssignationMassiqueForm
from .decorators import admin_required, rh_required, employe_required, safe_user_access
from .user_management import GestionnaireUtilisateurs, obtenir_role_utilisateur
from .audit import audit_action, log_calculation, log_data_change, log_security_event

"""
    
    print("Imports corrigés préparés.")
    print("Pour appliquer ces corrections, utilisez l'outil de remplacement de fichier.")
    return imports_corriges

if __name__ == "__main__":
    nettoyer_imports_views()
