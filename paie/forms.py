from django import forms
from django.contrib.auth.models import User
from .models import RubriquePersonnalisee, EmployeRubrique, Employe, Site, Departement
from datetime import date

class EmployeForm(forms.ModelForm):
    """Formulaire pour créer/modifier un employé"""
    
    # Champs utilisateur
    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        max_length=128,
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Laisser vide pour conserver le mot de passe actuel"
    )
    
    class Meta:
        model = Employe
        fields = [
            'matricule', 'nom', 'prenom', 'fonction', 'salaire_base',
            'date_embauche', 'site', 'departement', 'telephone', 'actif'
        ]
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'salaire_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'site': forms.Select(attrs={'class': 'form-select'}),
            'departement': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.instance_user = kwargs.pop('instance_user', None)
        super().__init__(*args, **kwargs)
        
        # Pré-remplir les champs utilisateur si modification
        if self.instance_user:
            self.fields['username'].initial = self.instance_user.username
            self.fields['email'].initial = self.instance_user.email
            self.fields['password'].required = False
    
    def save(self, commit=True):
        employe = super().save(commit=False)
        
        if commit:
            # Créer ou mettre à jour l'utilisateur
            if self.instance_user:
                # Modification
                user = self.instance_user
                user.username = self.cleaned_data['username']
                user.email = self.cleaned_data['email']
                if self.cleaned_data['password']:
                    user.set_password(self.cleaned_data['password'])
                user.save()
            else:
                # Création
                user = User.objects.create_user(
                    username=self.cleaned_data['username'],
                    email=self.cleaned_data['email'],
                    password=self.cleaned_data['password'] or 'temp123'
                )
            
            employe.user = user
            employe.save()
        
        return employe

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