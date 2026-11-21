
from datetime import datetime

from django.shortcuts import (
    render, redirect, get_object_or_404
)
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, IntegrityError, OperationalError
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    DoctorProfile,
    Specialization,
    AvailabilitySlot,
    PatientProfile,
    Appointment,
)

from .forms import (
    PatientRegistrationForm,
    AvailabilitySlotForm,
)


# -----------------------------------
# HELPER FUNCTIONS
# -----------------------------------

def slot_datetime(slot, use_end=False):
    selected_time = (
        slot.end_time if use_end else slot.start_time
    )

    return timezone.make_aware(
        datetime.combine(slot.date, selected_time),
        timezone.get_current_timezone()
    )


def is_future_slot(slot):
    return slot_datetime(slot) > timezone.now()


def has_ended(slot):
    return slot_datetime(slot, use_end=True) <= timezone.now()


def access_denied(request):
    return render(
        request,
        'core/access_denied.html',
        status=403
    )


def get_doctor(request):
    return DoctorProfile.objects.filter(
        user=request.user
    ).select_related(
        'user', 'specialization'
    ).first()


# -----------------------------------
# HOME
# -----------------------------------

def home(request):
    return render(request, 'core/home.html')


# -----------------------------------
# ROLE-BASED DASHBOARD
# -----------------------------------

@login_required
def role_dashboard(request):

    if DoctorProfile.objects.filter(
        user=request.user
    ).exists():
        return redirect('doctor_dashboard')

    if PatientProfile.objects.filter(
        user=request.user
    ).exists():
        return redirect('patient_dashboard')

    if request.user.is_staff:
        return redirect('admin:index')

    return access_denied(request)


# -----------------------------------
# FIND DOCTORS + SEARCH AND FILTER
# -----------------------------------

def doctor_list(request):

    search_query = request.GET.get('search', '').strip()
    specialization_id = request.GET.get(
        'specialization', ''
    ).strip()

    specializations = Specialization.objects.all().order_by(
        'name'
    )

    doctors = DoctorProfile.objects.filter(
        is_approved=True
    ).select_related(
        'user', 'specialization'
    ).annotate(
        full_name=Concat(
            'user__first_name',
            Value(' '),
            'user__last_name'
        )
    )

    # Search by first name, last name,
    # full name, or username.
    if search_query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__username__icontains=search_query)
            | Q(full_name__icontains=search_query)
        )

    # Filter by medical specialization.
    if specialization_id.isdigit():
        doctors = doctors.filter(
            specialization_id=int(specialization_id)
        )
    elif specialization_id:
        specialization_id = ''

    doctors = list(
        doctors.order_by('user__first_name', 'user__last_name')
    )

    # Find slots with active or completed bookings.
    booked_ids = Appointment.objects.filter(
        status__in=['booked', 'completed']
    ).values_list('slot_id', flat=True)

    available_slots = AvailabilitySlot.objects.filter(
        doctor__in=doctors,
        is_active=True,
        date__gte=timezone.localdate()
    ).exclude(
        id__in=booked_ids
    ).order_by('date', 'start_time')

    available_slots = [
        slot for slot in available_slots
        if is_future_slot(slot)
    ]

    # Group slots by their doctor.
    slots_by_doctor = {}

    for slot in available_slots:
        slots_by_doctor.setdefault(
            slot.doctor_id, []
        ).append(slot)

    for doctor in doctors:
        doctor.available_slots = slots_by_doctor.get(
            doctor.id, []
        )

    return render(request, 'core/doctor_list.html', {
        'doctors': doctors,
        'specializations': specializations,
        'search_query': search_query,
        'selected_specialization': specialization_id,
    })


# -----------------------------------
# PATIENT REGISTRATION
# -----------------------------------

def register_patient(request):

    if request.user.is_authenticated:
        return redirect('role_dashboard')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                PatientProfile.objects.create(user=user)

            login(request, user)

            messages.success(
                request,
                "Registration successful! Welcome to MediCare."
            )

            return redirect('patient_dashboard')

    else:
        form = PatientRegistrationForm()

    return render(request, 'core/register.html', {
        'form': form
    })


# -----------------------------------
# PATIENT DASHBOARD
# -----------------------------------

@login_required
def patient_dashboard(request):

    patient = PatientProfile.objects.filter(
        user=request.user
    ).first()

    if patient is None:
        return access_denied(request)

    appointments = patient.appointments.select_related(
        'slot__doctor__user',
        'slot__doctor__specialization'
    ).all()

    for appointment in appointments:
        appointment.can_manage = (
            appointment.status == 'booked'
            and is_future_slot(appointment.slot)
        )

    return render(request, 'core/patient_dashboard.html', {
        'patient': patient,
        'appointments': appointments,
    })


# -----------------------------------
# BOOK APPOINTMENT
# -----------------------------------

@login_required
@require_POST
def book_appointment(request, slot_id):

    patient = PatientProfile.objects.filter(
        user=request.user
    ).first()

    if patient is None:
        return access_denied(request)

    slot = get_object_or_404(
        AvailabilitySlot.objects.select_related('doctor'),
        id=slot_id
    )

    if not slot.is_active or not slot.doctor.is_approved:
        messages.error(
            request,
            "This appointment slot is unavailable."
        )
        return redirect('doctor_list')

    if not is_future_slot(slot):
        messages.error(
            request,
            "Cannot book an appointment in the past."
        )
        return redirect('doctor_list')

    try:
        with transaction.atomic():
            Appointment.objects.create(
                patient=patient,
                slot=slot,
                status='booked'
            )

    except (IntegrityError, OperationalError):
        messages.error(
            request,
            "This slot is already booked or temporarily unavailable."
        )
        return redirect('doctor_list')

    messages.success(
        request,
        "Appointment booked successfully!"
    )

    return redirect('patient_dashboard')


# -----------------------------------
# CANCEL APPOINTMENT
# -----------------------------------

@login_required
@require_POST
def cancel_appointment(request, appointment_id):

    patient = PatientProfile.objects.filter(
        user=request.user
    ).first()

    if patient is None:
        return access_denied(request)

    try:
        with transaction.atomic():
            appointment = get_object_or_404(
                Appointment.objects.select_for_update()
                .select_related('slot'),
                id=appointment_id,
                patient=patient
            )

            if (
                appointment.status != 'booked'
                or not is_future_slot(appointment.slot)
            ):
                messages.error(
                    request,
                    "This appointment cannot be cancelled."
                )
                return redirect('patient_dashboard')

            appointment.status = 'cancelled'
            appointment.save(update_fields=['status'])

    except OperationalError:
        messages.error(
            request,
            "Could not cancel the appointment. Please try again."
        )
        return redirect('patient_dashboard')

    messages.success(
        request,
        "Your appointment has been cancelled successfully."
    )

    return redirect('patient_dashboard')


# -----------------------------------
# RESCHEDULE APPOINTMENT
# -----------------------------------

@login_required
def reschedule_appointment(request, appointment_id):

    patient = PatientProfile.objects.filter(
        user=request.user
    ).first()

    if patient is None:
        return access_denied(request)

    appointment = get_object_or_404(
        Appointment.objects.select_related(
            'slot__doctor__user'
        ),
        id=appointment_id,
        patient=patient
    )

    if (
        appointment.status != 'booked'
        or not is_future_slot(appointment.slot)
    ):
        messages.error(
            request,
            "This appointment cannot be rescheduled."
        )
        return redirect('patient_dashboard')

    doctor = appointment.slot.doctor

    if request.method == 'POST':

        slot_id = request.POST.get('slot_id')

        if not slot_id:
            messages.error(
                request,
                "Please select an appointment slot."
            )
            return redirect(
                'reschedule_appointment',
                appointment_id=appointment.id
            )

        new_slot = get_object_or_404(
            AvailabilitySlot,
            id=slot_id,
            doctor=doctor
        )

        if (
            not new_slot.is_active
            or not doctor.is_approved
            or not is_future_slot(new_slot)
        ):
            messages.error(
                request,
                "The selected slot is no longer available."
            )
            return redirect(
                'reschedule_appointment',
                appointment_id=appointment.id
            )

        if new_slot.id == appointment.slot_id:
            messages.error(
                request,
                "Please select a different appointment slot."
            )
            return redirect(
                'reschedule_appointment',
                appointment_id=appointment.id
            )

        try:
            with transaction.atomic():

                locked_appointment = (
                    Appointment.objects.select_for_update()
                    .select_related('slot')
                    .get(
                        id=appointment.id,
                        patient=patient
                    )
                )

                if (
                    locked_appointment.status != 'booked'
                    or not is_future_slot(locked_appointment.slot)
                ):
                    messages.error(
                        request,
                        "This appointment can no longer be rescheduled."
                    )
                    return redirect('patient_dashboard')

                locked_appointment.slot = new_slot
                locked_appointment.save(
                    update_fields=['slot']
                )

        except (IntegrityError, OperationalError):
            messages.error(
                request,
                "That slot is booked or temporarily unavailable."
            )
            return redirect(
                'reschedule_appointment',
                appointment_id=appointment.id
            )

        messages.success(
            request,
            "Appointment rescheduled successfully!"
        )
        return redirect('patient_dashboard')

    booked_ids = Appointment.objects.filter(
        status__in=['booked', 'completed']
    ).values_list('slot_id', flat=True)

    available_slots = AvailabilitySlot.objects.filter(
        doctor=doctor,
        is_active=True,
        date__gte=timezone.localdate()
    ).exclude(
        id__in=booked_ids
    ).order_by('date', 'start_time')

    available_slots = [
        slot for slot in available_slots
        if is_future_slot(slot)
    ]

    return render(request, 'core/reschedule.html', {
        'appointment': appointment,
        'doctor': doctor,
        'available_slots': available_slots,
    })


# -----------------------------------
# DOCTOR DASHBOARD
# -----------------------------------

@login_required
def doctor_dashboard(request):

    doctor = get_doctor(request)

    if doctor is None:
        return access_denied(request)

    appointments = list(
        Appointment.objects.filter(
            slot__doctor=doctor
        ).select_related(
            'patient__user',
            'slot'
        ).order_by(
            'slot__date',
            'slot__start_time'
        )
    )

    upcoming = []
    history = []

    for appointment in appointments:
        if (
            appointment.status == 'booked'
            and is_future_slot(appointment.slot)
        ):
            upcoming.append(appointment)
        else:
            history.append(appointment)

    history.reverse()

    slots = list(
        AvailabilitySlot.objects.filter(
            doctor=doctor,
            date__gte=timezone.localdate()
        ).order_by('date', 'start_time')
    )

    active_bookings = {
        appointment.slot_id: appointment
        for appointment in appointments
        if appointment.status in ['booked', 'completed']
    }

    upcoming_slots = []

    for slot in slots:
        if not is_future_slot(slot):
            continue

        booking = active_bookings.get(slot.id)

        if booking:
            slot.display_status = 'Booked'
            slot.can_deactivate = False
        elif slot.is_active:
            slot.display_status = 'Available'
            slot.can_deactivate = True
        else:
            slot.display_status = 'Inactive'
            slot.can_deactivate = False

        upcoming_slots.append(slot)

    return render(request, 'core/doctor_dashboard.html', {
        'doctor': doctor,
        'upcoming_appointments': upcoming,
        'past_appointments': history,
        'upcoming_slots': upcoming_slots,
        'total_appointments': len(appointments),
        'upcoming_count': len(upcoming),
        'completed_count': sum(
            a.status == 'completed'
            for a in appointments
        ),
        'cancelled_count': sum(
            a.status == 'cancelled'
            for a in appointments
        ),
    })


# -----------------------------------
# ADD AVAILABILITY SLOT
# -----------------------------------

@login_required
def add_availability(request):

    doctor = get_doctor(request)

    if doctor is None:
        return access_denied(request)

    if request.method == 'POST':
        form = AvailabilitySlotForm(
            request.POST,
            doctor=doctor
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    slot = form.save(commit=False)
                    slot.doctor = doctor
                    slot.is_active = True
                    slot.save()

            except (IntegrityError, OperationalError):
                form.add_error(
                    None,
                    "Could not save this slot. Please try again."
                )
            else:
                messages.success(
                    request,
                    "Availability slot added successfully!"
                )
                return redirect('doctor_dashboard')

    else:
        form = AvailabilitySlotForm(
            doctor=doctor
        )

    return render(request, 'core/add_availability.html', {
        'doctor': doctor,
        'form': form,
    })


# -----------------------------------
# DEACTIVATE AVAILABILITY SLOT
# -----------------------------------

@login_required
@require_POST
def deactivate_slot(request, slot_id):

    doctor = get_doctor(request)

    if doctor is None:
        return access_denied(request)

    try:
        with transaction.atomic():

            slot = get_object_or_404(
                AvailabilitySlot.objects.select_for_update(),
                id=slot_id,
                doctor=doctor
            )

            if not slot.is_active or not is_future_slot(slot):
                messages.error(
                    request,
                    "This slot cannot be deactivated."
                )
                return redirect('doctor_dashboard')

            has_booking = Appointment.objects.filter(
                slot=slot,
                status__in=['booked', 'completed']
            ).exists()

            if has_booking:
                messages.error(
                    request,
                    "Cannot deactivate an already booked slot."
                )
                return redirect('doctor_dashboard')

            slot.is_active = False
            slot.save(update_fields=['is_active'])

    except OperationalError:
        messages.error(
            request,
            "Unable to update the slot. Please try again."
        )
        return redirect('doctor_dashboard')

    messages.success(
        request,
        "Appointment slot deactivated successfully."
    )

    return redirect('doctor_dashboard')


# -----------------------------------
# MARK APPOINTMENT COMPLETED
# -----------------------------------

@login_required
@require_POST
def complete_appointment(request, appointment_id):

    doctor = get_doctor(request)

    if doctor is None:
        return access_denied(request)

    try:
        with transaction.atomic():

            appointment = get_object_or_404(
                Appointment.objects.select_for_update()
                .select_related('slot'),
                id=appointment_id,
                slot__doctor=doctor
            )

            if appointment.status != 'booked':
                messages.error(
                    request,
                    "Only booked appointments can be completed."
                )
                return redirect('doctor_dashboard')

            if not has_ended(appointment.slot):
                messages.error(
                    request,
                    "The appointment must finish before it can be marked completed."
                )
                return redirect('doctor_dashboard')

            appointment.status = 'completed'
            appointment.save(update_fields=['status'])

    except OperationalError:
        messages.error(
            request,
            "Unable to update the appointment. Please try again."
        )
        return redirect('doctor_dashboard')

    messages.success(
        request,
        "Appointment marked as completed!"
    )

    return redirect('doctor_dashboard')
