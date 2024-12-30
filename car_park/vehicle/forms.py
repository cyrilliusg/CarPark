# forms.py
from django import forms
from timezone_field import TimeZoneFormField
from .models import Enterprise, Vehicle

class EnterpriseForm(forms.ModelForm):
    local_timezone = TimeZoneFormField(label="Таймзона", required=False)

    class Meta:
        model = Enterprise
        fields = ['name', 'city', 'local_timezone']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ['enterprise', 'drivers']  # enterprise задаём из URL, drivers пока не трогаем
