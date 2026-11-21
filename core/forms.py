
from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone

from .models import AvailabilitySlot


# -----------------------------------
# PATIENT REGISTRATION FORM
# -----------------------------------

class PatientRegistrationForm(UserCreationForm):

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


# -----------------------------------
# DOCTOR AVAILABILITY FORM
# -----------------------------------

class AvailabilitySlotForm(forms.ModelForm):

    class Meta:
        model = AvailabilitySlot
        fields = [
            'date',
            'start_time',
            'end_time',
        ]

        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d'
            ),

            'start_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                },
                format='%H:%M'
            ),

            'end_time': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                },
                format='%H:%M'
            ),
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.doctor = doctor

    def clean(self):
        cleaned_data = super().clean()

        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not all([date, start_time, end_time]):
            return cleaned_data

        if end_time <= start_time:
            raise forms.ValidationError(
                "End time must be later than start time."
            )

        start_datetime = timezone.make_aware(
            datetime.combine(date, start_time),
            timezone.get_current_timezone()
        )

        if start_datetime <= timezone.now():
            raise forms.ValidationError(
                "You cannot create an appointment slot in the past."
            )

        if self.doctor is None:
            raise forms.ValidationError(
                "A doctor is required."
            )

        # Check overlapping active slots
        overlapping_slots = AvailabilitySlot.objects.filter(
            doctor=self.doctor,
            date=date,
            is_active=True,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )

        if self.instance.pk:
            overlapping_slots = overlapping_slots.exclude(
                pk=self.instance.pk
            )

        if overlapping_slots.exists():
            raise forms.ValidationError(
                "This time overlaps with another active slot."
            )

        return cleaned_data
