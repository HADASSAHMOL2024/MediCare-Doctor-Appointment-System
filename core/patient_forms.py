
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import PatientProfile


# -----------------------------------
# PATIENT ACCOUNT FORM
# -----------------------------------

class PatientUserForm(forms.ModelForm):

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
                "This email address is already registered."
            )

        return email


# -----------------------------------
# PATIENT PROFILE FORM
# -----------------------------------

class PatientProfileForm(forms.ModelForm):

    class Meta:
        model = PatientProfile

        fields = [
            'phone',
            'date_of_birth',
            'address',
        ]

        widgets = {
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter your phone number',
                }
            ),

            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d'
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Enter your address',
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()

        if phone:
            normalized = phone.replace(' ', '').replace('-', '')

            if normalized.startswith('+'):
                digits = normalized[1:]
            else:
                digits = normalized

            if not digits.isdigit() or not (7 <= len(digits) <= 14):
                raise forms.ValidationError(
                    "Enter a valid phone number with 7 to 14 digits."
                )

        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')

        if dob and dob > timezone.localdate():
            raise forms.ValidationError(
                "Date of birth cannot be in the future."
            )

        return dob
