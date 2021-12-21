# from core.bascula.models import  Chofer, Cliente,  Producto, Vehiculo
from django import forms

class ReportForm(forms.Form):
    # Extra Fields
    date_range = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))
    time_range_in = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))
    time_range_out = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'autocomplete': 'off'
    }))

    # cliente = forms.ModelChoiceField(queryset=Cliente.objects.filter(activo__exact=True).order_by('denominacion'), empty_label="(Todos)")
    # producto = forms.ModelChoiceField(queryset=Producto.objects.filter(activo__exact=True).order_by('denominacion'), empty_label="(Todos)")
    # vehiculo = forms.ModelChoiceField(queryset=Vehiculo.objects.filter(activo__exact=True).order_by('matricula'), empty_label="(Todos)")
    # chofer = forms.ModelChoiceField(queryset=Chofer.objects.filter(activo__exact=True).order_by('nombre','apellido'), empty_label="(Todos)")
   
    # cliente.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    # producto.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    # vehiculo.widget.attrs.update({'class': 'form-control select2','multiple':'true'})
    # chofer.widget.attrs.update({'class': 'form-control select2','multiple':'true'})    