from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Lojista, RamoAtividade, AdesaoLojista, Localizacao
from localflavor.br.forms import *

class LojistaRegistrationForm(forms.ModelForm):
    CNPJLojista = BRCNPJField(label='CNPJ*', required=True, max_length=18, widget=forms.TextInput(attrs={'class':'cnpj'}))
    ramoAtividade =  forms.Select(attrs={'class':'form-group'}) 
    localizacao = forms.ModelChoiceField(
        queryset=Localizacao.objects.all(),
        required=False,
        label='Localização',
        help_text='Selecione a localização associada ao lojista'
    )
    class Meta:
        model = Lojista
        fields = '__all__'
        widgets = {
            'ativo': forms.HiddenInput,
            'CadastradoPor': forms.HiddenInput,
        }

    def clean_CNPJLojista(self):
        CNPJLojista = self.cleaned_data.get('CNPJLojista')
        CNPJLojista_qs = Lojista.objects.filter(CNPJLojista=CNPJLojista)
        if CNPJLojista_qs.exists():
            raise ValidationError("CNPJ do lojista não cadastrado!")
        return CNPJLojista

class RamoAtividadeRegistrationForm(forms.ModelForm):

    class Meta:
        model = RamoAtividade
        fields = '__all__'
        widgets = {
            'CadastradoPor': forms.HiddenInput,
        }
        
class LocalizacaoRegistrationForm(forms.ModelForm):

    class Meta:
        model = Localizacao
        fields = '__all__'
        widgets = {
            'CadastradoPor': forms.HiddenInput,
        }
        
class FormLojistaAdesao(forms.ModelForm):    
    class Meta:
        model = AdesaoLojista
        fields = '__all__'
