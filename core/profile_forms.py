
from django import forms
from django.contrib.auth.models import User

from .models import DoctorProfile


# -----------------------------------
# DOCTOR ACCOUNT FORM
# -----------------------------------

class DoctorUserForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'email',
        ]

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()

        if not email:
            raise forms.ValidationError(
                "Email address is required."
            )

        if User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError(
                "This email address is already in use."
            )

        return email


# -----------------------------------
# DOCTOR PROFILE FORM
# -----------------------------------

class DoctorProfileForm(forms.ModelForm):

    class Meta:
        model = DoctorProfile

        fields = [
            'qualification',
            'experience',
            'consultation_fee',
            'bio',
        ]

        widgets = {
            'qualification': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'experience': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0,
                }
            ),

            'consultation_fee': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0,
                    'step': '0.01',
                }
            ),

            'bio': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                }
            ),
        }

    def clean_consultation_fee(self):
        fee = self.cleaned_data['consultation_fee']

        if fee < 0:
            raise forms.ValidationError(
                "Consultation fee cannot be negative."
            )

        return fee
