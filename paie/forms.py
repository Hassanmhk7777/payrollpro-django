from django import forms
from .models import RubriquePersonnalisee, EmployeRubrique, Employe
from datetime import date

class RubriqueRapideForm(forms.Form):
    """Formulaire pour créer rapidement une rubrique ponctuelle"""
    
    employe = forms.ModelChoiceField(
        queryset=Employe.objects.filter(actif=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nom_rubrique = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Prime exceptionnelle'})
    )
    type_rubrique = forms.ChoiceField(
        choices=RubriquePersonnalisee.TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    montant = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    commentaire = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    mois = forms.IntegerField(
        min_value=1,
        max_value=12,
        initial=date.today().month,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    annee = forms.IntegerField(
        min_value=2020,
        max_value=2030,
        initial=date.today().year,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class AssignationMassiqueForm(forms.Form):
    """Formulaire pour assignation massive de rubriques"""
    
    rubrique = forms.ModelChoiceField(
        queryset=RubriquePersonnalisee.objects.filter(actif=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    employes = forms.ModelMultipleChoiceField(
        queryset=Employe.objects.filter(actif=True),
        widget=forms.CheckboxSelectMultiple()
    )
    montant_personnalise = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    date_debut = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    commentaire = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )