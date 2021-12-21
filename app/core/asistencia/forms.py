
from django.forms import *
from django import forms
from core.base.forms import *
from .models import *
''' 
=============================
===    RELOJ              ===
============================= '''
class RelojForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['denominacion'].widget.attrs['autofocus'] = True

    class Meta:
        model = Reloj
        fields = '__all__'
        exclude = readonly_fields
        widgets = {
            'denominacion': forms.TextInput(attrs={'placeholder': 'Ingrese Denominacion Reloj'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data
''' 
=============================
===       MARCACION       ===
============================= '''
class MarcacionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['denominacion'].widget.attrs['autofocus'] = True

    class Meta:
        model = Marcacion
        fields = '__all__'
        exclude = readonly_fields
        widgets = {
            # 'denominacion': forms.TextInput(attrs={'placeholder': 'Ingrese Denominacion Marcacion'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data

''' 
=============================
=== MARCACION DETALLE     ===
============================= '''
class MarcacionDetalleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['denominacion'].widget.attrs['autofocus'] = True

    class Meta:
        model = MarcacionDetalle
        fields = '__all__'
        exclude = readonly_fields
        widgets = {
            # 'denominacion': forms.TextInput(attrs={'placeholder': 'Ingrese Denominacion Marcacion'}),
        }

    def save(self, commit=True):
        data = {}
        try:
            if self.is_valid():
                super().save()
            else:
                data['error'] = self.errors
        except Exception as e:
            data['error'] = str(e)
        return data