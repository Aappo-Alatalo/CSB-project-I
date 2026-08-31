from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Reservation


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    apartment = forms.CharField(max_length=10, help_text='For example A 12')
    phone = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username']


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'slot', 'note']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date')
        slot = cleaned.get('slot')
        if date and slot and Reservation.objects.filter(date=date, slot=slot).exists():
            raise forms.ValidationError('That shift is already reserved.')
        return cleaned
