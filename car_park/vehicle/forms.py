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
    purchase_datetime = forms.DateTimeField(
        label="Дата/время покупки (UTC)",
        widget=forms.TextInput(
            attrs={
                # Можно присвоить класс и ID, если планируем обращаться именно к ним
                'id': 'purchase_datetime_picker',
                'class': 'form-control',
                'autocomplete': 'off',
                # можно добавить data-атрибуты, но это опционально, см. вёрстку ниже
            }
        )
    )

    class Meta:
        model = Vehicle
        # Пусть остальные поля не трогаем,
        # или исключаем, или выводим явно
        exclude = ['enterprise', 'drivers']

class TripUploadForm(forms.Form):
    vehicle = forms.ModelChoiceField(queryset=Vehicle.objects.all(), label='Машина')
    start_time = forms.DateTimeField(
        label='Начало поездки',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    end_time = forms.DateTimeField(
        label='Окончание поездки',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    gpx_file = forms.FileField(label='GPX файл')