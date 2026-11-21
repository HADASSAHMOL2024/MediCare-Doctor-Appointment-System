
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from . import profile_views
from . import patient_views


urlpatterns = [

    # HOME
    path(
        '',
        views.home,
        name='home'
    ),

    # FIND DOCTORS
    path(
        'doctors/',
        views.doctor_list,
        name='doctor_list'
    ),

    # PATIENT REGISTRATION
    path(
        'register/',
        views.register_patient,
        name='register'
    ),

    # LOGIN
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='core/login.html'
        ),
        name='login'
    ),

    # LOGOUT
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # ROLE-BASED DASHBOARD
    path(
        'my-dashboard/',
        views.role_dashboard,
        name='role_dashboard'
    ),

    # PATIENT DASHBOARD
    path(
        'dashboard/',
        views.patient_dashboard,
        name='patient_dashboard'
    ),

    # EDIT PATIENT PROFILE
    path(
        'patient/profile/edit/',
        patient_views.edit_patient_profile,
        name='edit_patient_profile'
    ),

    # DOCTOR DASHBOARD
    path(
        'doctor/dashboard/',
        views.doctor_dashboard,
        name='doctor_dashboard'
    ),

    # EDIT DOCTOR PROFILE
    path(
        'doctor/profile/edit/',
        profile_views.edit_doctor_profile,
        name='edit_doctor_profile'
    ),

    # BOOK APPOINTMENT
    path(
        'book/<int:slot_id>/',
        views.book_appointment,
        name='book_appointment'
    ),

    # CANCEL APPOINTMENT
    path(
        'cancel/<int:appointment_id>/',
        views.cancel_appointment,
        name='cancel_appointment'
    ),

    # RESCHEDULE APPOINTMENT
    path(
        'reschedule/<int:appointment_id>/',
        views.reschedule_appointment,
        name='reschedule_appointment'
    ),

    # ADD DOCTOR AVAILABILITY
    path(
        'doctor/availability/add/',
        views.add_availability,
        name='add_availability'
    ),

    # DEACTIVATE AVAILABILITY
    path(
        'doctor/availability/<int:slot_id>/deactivate/',
        views.deactivate_slot,
        name='deactivate_slot'
    ),

    # COMPLETE APPOINTMENT
    path(
        'doctor/appointment/<int:appointment_id>/complete/',
        views.complete_appointment,
        name='complete_appointment'
    ),
]
