
# MediCare — Doctor Appointment Booking System

A Django-based web application for managing doctor appointments with separate patient, doctor, and administrator modules.

## Overview

MediCare simplifies appointment scheduling by allowing patients to discover approved doctors, select available consultation slots, and manage their appointments online.

Doctors can maintain their availability, view appointments, and update their professional profiles.

Administrators can manage user accounts, doctor profiles, specializations, and approval status using Django Admin.

## Features

### Patient Module
- Patient registration and login
- Search doctors by name and specialization
- View approved doctor profiles
- Book available consultation slots
- Reschedule or cancel appointments
- View appointment history
- Update patient profile

### Doctor Module
- Doctor dashboard
- View scheduled appointments
- Add and deactivate availability slots
- Validation for overlapping time slots
- Mark eligible appointments as completed
- Update professional profile

### Administrator Module
- Django Admin dashboard
- Manage users and doctor profiles
- Approve doctor accounts
- Manage medical specializations
- View appointment and availability records

## Technology Stack

- Python
- Django 5.2
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

## Project Structure

```text
DoctorAppointmentSystem/
├── core/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── patient_forms.py
│   ├── patient_views.py
│   ├── profile_forms.py
│   └── profile_views.py
├── hospital_booking/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/MediCare-Doctor-Appointment-System.git
cd MediCare-Doctor-Appointment-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=your-own-secure-django-secret-key
DJANGO_DEBUG=True
```

Generate a key using:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Do not commit your `.env` file.

### 5. Prepare the database

```bash
python manage.py migrate
```

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Application Routes

| Route | Description |
| --- | --- |
| `/` | Homepage |
| `/admin/` | Django administration |
| `/doctors/` | Doctor listing |
| `/patient/profile/edit/` | Edit patient profile |
| `/doctor/profile/edit/` | Edit doctor profile |

## Database

The application uses Django ORM and SQLite.

Its main application models are:

- Specialization
- PatientProfile
- DoctorProfile
- AvailabilitySlot
- Appointment

Django's built-in User model handles authentication.

## Future Enhancements

- Email-based password recovery
- Appointment reminders
- Online payments
- Doctor self-registration with administrator approval
- Cloud deployment
- Expanded automated testing

## Project Status

Completed as an academic Django project and successfully demonstrated during evaluation.

## License

No license has been assigned yet. All rights reserved.
