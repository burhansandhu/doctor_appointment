from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from . import models
from doctor.models import Doctor,Availability
from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth import login,logout,authenticate
# Create your views here.
def patient_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        image = request.FILES.get('image')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken")
            return render(request, 'patient_signup.html')

        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            models.Patient.objects.create(
                user=user,
                dob=dob,
                gender=gender,
                phone=phone,
                address=address,
                image=image
            )
            user.save
            messages.success(request, "Sign up successful! Please log in.")
            return redirect('patient_login')
        except Exception as e:
            messages.error(request, f"Error in sign up: {str(e)}")
            return render(request, 'patient_signup.html')
    
    return render(request, 'patient_signup.html')

def patient_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'doctor_login.html')
    return render(request,'patient_login.html')

@login_required(login_url='/patient/Plogin/')
def patient_dashboard(request):
    patient = models.Patient.objects.get(user=request.user)

    context = {
        'patient': patient
    }
    return render(request,'patient_dashboard.html',context)


@login_required(login_url='/patient/Plogin/')
def patient_update(request):
    patient = models.Patient.objects.get(user=request.user)
    if request.method == 'POST':
        patient.user.username = request.POST.get('username')
        patient.user.email = request.POST.get('email')
        patient.dob = request.POST.get('dob')
        patient.phone = request.POST.get('phone')
        patient.address = request.POST.get('address')
        #patient.image = request.FILES.get('image')
        if request.FILES.get('image'):
            patient.image = request.FILES.get('image')

        patient.user.save()
        patient.save()
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('patient_dashboard')
    context = {
        'patient': patient
        }
    return render(request, 'patient_update.html', context)
    

@login_required(login_url='/patient/Plogin/')
def request_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_datetime_str = request.POST.get('appointment_date')
        appointment_datetime_naive = datetime.fromisoformat(appointment_datetime_str)
        # Make appointment_datetime aware
        
        appointment_datetime = timezone.make_aware(appointment_datetime_naive, timezone.get_current_timezone())

        current_datetime = timezone.now()

        # Ensure the appointment date is today or in the future
        if appointment_datetime < current_datetime:
            messages.error(request, 'You cannot request an appointment in the past.')
            return redirect('appointment_request')
        
        doctor = get_object_or_404(Doctor, id=doctor_id)
        patient = get_object_or_404(models.Patient, user=request.user)

        appointment_day = appointment_datetime.strftime('%A')
        availability = doctor.availabilities.filter(day_of_week=appointment_day).first()

        if not availability:
            messages.error(request, f'Dr. {doctor.user.username} is not available on {appointment_day}.')
            return redirect('appointment_request')

        if appointment_datetime.time() < availability.start_time or appointment_datetime.time() > availability.end_time:
            messages.error(request, f'The selected time is outside Dr. {doctor.user.username}\'s available hours on {appointment_day}.')
            return redirect('appointment_request')

        models.Appointment.objects.create(
            doctor=doctor,
            patient=patient,
            appointment_date=appointment_datetime,
            status='PENDING'
        )

        subject = 'New Appointment Request'
        message = f'You have a new appointment request from {patient.user.username} on {appointment_datetime.strftime("%Y-%m-%d %H:%M:%S")}.'
        recipient_list = [doctor.user.email]
        from_email = patient.user.email

        send_mail(
            subject,
            message,
            from_email,  # Use patient's email as the sender
            recipient_list,
            fail_silently=False,
        )
        messages.success(request, 'Your appointment request has been sent to the doctor.')
        return redirect('patient_dashboard')

    doctors = Doctor.objects.all()
    return render(request, 'appointment_request.html', {'doctors': doctors})


@login_required(login_url='/patient/Plogin/')
def doctor_availability(request):
    doctors = Doctor.objects.prefetch_related('availabilities').all()

    return render(request, 'doctor_availability.html', {'doctors': doctors})


@login_required(login_url='/patient/Plogin/')
def view_requests(request):
    try:
        patient = models.Patient.objects.get(user=request.user)
    except models.Patient.DoesNotExist:
        # Handle the case where the Patient instance is not found
        return render(request, 'view_requests.html', {'requests': []})
    requests = models.Appointment.objects.filter(patient=patient)
    
    context = {
        'requests': requests,
    }
    
    
    return render(request, 'view_requests.html', context)


@login_required(login_url='/patient/Plogin/')
def patient_cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(models.Appointment, id=appointment_id)
    
    if request.user != appointment.patient.user:
        messages.error(request, "You are not authorized to cancel this appointment.")
        return redirect('patient_dashboard')

    if appointment.status in ['ACCEPTED', 'PENDING']:
        appointment.status = 'CANCELED'
        appointment.save()
        send_mail(
            'Appointment Canceled',
            f'Patient {request.user.username} has canceled the appointment scheduled for {appointment.appointment_date.strftime("%Y-%m-%d %H:%M")}.',
            request.user.email,  # Send from the patient's email (optional, based on preference)
            [appointment.doctor.user.email],
            fail_silently=False,
        )
        messages.success(request, "Appointment has been canceled.")
    else:
        messages.error(request, "You cannot cancel this appointment.")

    return redirect('view_requests')


def search_doctor(request):
    name_query = request.GET.get('name')
    specialization_query = request.GET.get('specialization')
    doctors = Doctor.objects.all()

    if name_query:
        doctors = doctors.filter(user__username__icontains=name_query)
    if specialization_query:
        doctors = doctors.filter(specialization__icontains=specialization_query)

    # Prepare data with availability
    doctor_data = []
    for doctor in doctors:
        availabilities = doctor.availabilities.all()  # Fetch related availabilities
        doctor_data.append({
            'name': f"Dr. {doctor.user.username}",
            'specialization': doctor.specialization,
            'availabilities': availabilities,
        })

    return render(request, 'search_doctor.html', {'doctor_data': doctor_data})



@login_required(login_url='/patient/Plogin/')
def patient_logout(request):
    logout(request)
    return redirect('patient_login')