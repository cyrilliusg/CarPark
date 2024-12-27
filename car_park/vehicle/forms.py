# forms.py
from django import forms
from timezone_field import TimeZoneFormField
from .models import Enterprise

class EnterpriseForm(forms.ModelForm):
    local_timezone = TimeZoneFormField(label="Таймзона", required=False)

    class Meta:
        model = Enterprise
        fields = ['name', 'city', 'local_timezone']
