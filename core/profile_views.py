
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import DoctorProfile

from .profile_forms import (
    DoctorUserForm,
    DoctorProfileForm,
)


# -----------------------------------
# EDIT DOCTOR PROFILE
# -----------------------------------

@login_required
def edit_doctor_profile(request):

    doctor = DoctorProfile.objects.filter(
        user=request.user
    ).select_related(
        'user',
        'specialization'
    ).first()

    # Only users with a doctor profile can edit it.
    if doctor is None:
        return render(
            request,
            'core/access_denied.html',
            status=403
        )

    if request.method == 'POST':

        user_form = DoctorUserForm(
            request.POST,
            instance=request.user,
            prefix='user'
        )

        profile_form = DoctorProfileForm(
            request.POST,
            instance=doctor,
            prefix='profile'
        )

        if user_form.is_valid() and profile_form.is_valid():

            with transaction.atomic():
                user_form.save()
                profile_form.save()

            messages.success(
                request,
                "Your doctor profile has been updated successfully!"
            )

            return redirect('doctor_dashboard')

    else:

        user_form = DoctorUserForm(
            instance=request.user,
            prefix='user'
        )

        profile_form = DoctorProfileForm(
            instance=doctor,
            prefix='profile'
        )

    return render(
        request,
        'core/edit_doctor_profile.html',
        {
            'doctor': doctor,
            'user_form': user_form,
            'profile_form': profile_form,
        }
    )
