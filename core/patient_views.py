
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import PatientProfile

from .patient_forms import (
    PatientUserForm,
    PatientProfileForm,
)


# -----------------------------------
# EDIT PATIENT PROFILE
# -----------------------------------

@login_required
def edit_patient_profile(request):

    patient = PatientProfile.objects.filter(
        user=request.user
    ).first()

    # Only registered patients can edit their profile.
    if patient is None:
        return render(
            request,
            'core/access_denied.html',
            status=403
        )

    if request.method == 'POST':

        user_form = PatientUserForm(
            request.POST,
            instance=request.user,
            prefix='user'
        )

        profile_form = PatientProfileForm(
            request.POST,
            instance=patient,
            prefix='profile'
        )

        if user_form.is_valid() and profile_form.is_valid():

            with transaction.atomic():
                user_form.save()
                profile_form.save()

            messages.success(
                request,
                "Your patient profile has been updated successfully!"
            )

            return redirect('patient_dashboard')

    else:

        user_form = PatientUserForm(
            instance=request.user,
            prefix='user'
        )

        profile_form = PatientProfileForm(
            instance=patient,
            prefix='profile'
        )

    return render(
        request,
        'core/edit_patient_profile.html',
        {
            'patient': patient,
            'user_form': user_form,
            'profile_form': profile_form,
        }
    )
