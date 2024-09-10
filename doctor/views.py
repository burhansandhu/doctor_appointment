from django.shortcuts import render,HttpResponse,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from . import models
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from datetime import datetime
from patient.models import Appointment
# Create your views here.
def doctor_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        specialization = request.POST.get('specialization')
        consultation_fee = request.POST.get('consultation_fee')
        profile_image = request.FILES.get('profile_image')
        days_of_week = request.POST.getlist('day_of_week')
        start_times = request.POST.getlist('start_time')
        end_times = request.POST.getlist('end_time')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken")
            return render(request, 'doctor_signup.html')
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
            except Exception as e:
                #messages.error(request, f"Error creating user: {e}")
                return render(request, 'doctor_signup.html', {'error': 'Error creating user'})

            try:
                doctor = models.Doctor(
                    user=user,
                    phone_number=phone_number,
                    specialization=specialization,
                    consultation_fee=consultation_fee,
                    profile_image=profile_image
                )
                doctor.save()


                if len(days_of_week) == len(start_times) == len(end_times):
                    for day, start, end in zip(days_of_week, start_times, end_times):
                        models.Availability.objects.create(
                            doctor=doctor,
                            day_of_week=day,
                            start_time=start,
                            end_time=end
                        )
                else:
                    print("Error: Mismatch in number of days, start times, or end times")
                messages.success(request, "Sign up successful! Please log in.")
                return redirect('doctor_login')
            except Exception as e:
                user.delete()
                #messages.error(request, f"Error creating doctor profile: {e}")
                return render(request, 'doctor_signup.html', {'error': 'Error creating doctor profile'})

            #messages.success(request, "Sign up successful! Please log in.")
            #return redirect('doctor_login')

    return render(request, 'doctor_signup.html')

def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('doctor_dashboard')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'doctor_login.html')
    return render(request,'doctor_login.html')

@login_required(login_url='/doctor/login/')
def doctor_dashboard(request):
    doctor = get_object_or_404(models.Doctor, user=request.user)
    availabilities = doctor.availabilities.all()

    context = {
        'doctor': doctor,
        'availabilities': availabilities,
    }
    return render(request, 'doctor_dashboard.html', context)



@login_required(login_url='/doctor/login/')
def update_doctor_profile(request):
    # Get the doctor's profile
    doctor = get_object_or_404(models.Doctor, user=request.user)

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')

        phone_number = request.POST.get('phone_number')
        specialization = request.POST.get('specialization')
        consultation_fee = request.POST.get('consultation_fee')
        profile_image = request.FILES.get('profile_image')

        # Update user details if provided
        user = request.user
        if username:
            user.username = username
        if email:
            user.email = email

        user.save()

        # Update doctor profile
        doctor.phone_number = phone_number
        doctor.specialization = specialization
        doctor.consultation_fee = consultation_fee
        if profile_image:
            doctor.profile_image = profile_image
        doctor.save()

        # Handle availability update
        days_of_week = request.POST.getlist('day_of_week')
        start_times = request.POST.getlist('start_time')
        end_times = request.POST.getlist('end_time')

        # Clear existing availability
        models.Availability.objects.filter(doctor=doctor, day_of_week__in=days_of_week).delete()

        if len(days_of_week) == len(start_times) == len(end_times):
            for day, start, end in zip(days_of_week, start_times, end_times):
                start_time = datetime.strptime(start, "%H:%M").time()
                end_time = datetime.strptime(end, "%H:%M").time()
                models.Availability.objects.create(
                    doctor=doctor,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time
                )
            messages.success(request, "Profile and availability updated successfully!")
            return redirect('doctor_dashboard')
        else:
            messages.error(request, "Mismatch in number of days, start times, or end times")

        return redirect('doctor_dashboard')
    
    # Prepare initial data for the form
    doctor_form_data = {
        'username': doctor.user.username,
        'email': doctor.user.email,
        'phone_number': doctor.phone_number,
        'specialization': doctor.specialization,
        'consultation_fee': doctor.consultation_fee,
    }

    availability_entries = models.Availability.objects.filter(doctor=doctor)
    
    return render(request, 'doctor_update.html', {
        'doctor_form_data': doctor_form_data,
        'availability_entries': availability_entries
    })


@login_required(login_url='/doctor/login/')
def pending_requests(request):
    doctor = get_object_or_404(models.Doctor, user=request.user)
    
    # Fetch pending appointment requests for the doctor
    pending_requests = Appointment.objects.filter(doctor=doctor, status='PENDING')
    
    context = {
        'pending_requests': pending_requests,
    }
    
    return render(request, 'pending_requests.html', context)


@login_required(login_url='/doctor/login/')
def accept_request(request,request_id):
    appointment = get_object_or_404(Appointment, id=request_id, doctor__user=request.user)
    appointment.status = 'ACCEPTED'
    appointment.save()

    doctor_name = appointment.doctor.user.username
    appointment_date = appointment.appointment_date.strftime('%Y-%m-%d %H:%M:%S')
    patient_email = appointment.patient.user.email

    # Send an email to the patient notifying them of the accepted appointment
    subject = 'Your Appointment Request Has Been Accepted'
    message = f'Hello {appointment.patient.user.username},\n\nYour appointment request with Dr. {doctor_name} on {appointment_date} has been accepted.\n\nThank you!'
    recipient_list = [patient_email]
    from_email = appointment.doctor.user.email  # This can be set to any default email address or the doctor's email

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
    return redirect('pending_requests')


@login_required(login_url='/doctor/login/')
def reject_request(request, request_id):
    appointment = get_object_or_404(Appointment, id=request_id, doctor__user=request.user)
    appointment.status = 'REJECTED'
    appointment.save()
    doctor_name = appointment.doctor.user.username
    appointment_date = appointment.appointment_date.strftime('%Y-%m-%d %H:%M:%S')
    patient_email = appointment.patient.user.email

    # Send an email to the patient notifying them of the accepted appointment
    subject = 'Your Appointment Request Has Been Rejected'
    message = f'Hello {appointment.patient.user.username},\n\nYour appointment request with Dr. {doctor_name} on {appointment_date} has been Rejected.\n\nThank you!'
    recipient_list = [patient_email]
    from_email = appointment.doctor.user.email  # This can be set to any default email address or the doctor's email

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,
    )
    return redirect('pending_requests')


@login_required(login_url='/doctor/login/')
def doctor_cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user != appointment.doctor.user:
        messages.error(request, "You are not authorized to cancel this appointment.")
        return redirect('doctor_dashboard')

    appointment.status = 'CANCELED'
    appointment.save()

    doctor_email = appointment.doctor.user.email
    send_mail(
        'Appointment Canceled',
        f'Your appointment with Dr. {appointment.doctor.user.username} on {appointment.appointment_date.strftime("%Y-%m-%d %H:%M")} has been canceled.',
        doctor_email,
        [appointment.patient.user.email],
        fail_silently=False,
    )

    messages.success(request, "Appointment canceled and patient notified.")
    return redirect('doctor_dashboard')



@login_required(login_url='/doctor/login/')
def accepted_requests_view(request):
    doctor = get_object_or_404(models.Doctor, user=request.user)
    # Filter accepted appointments for this doctor
    accepted_appointments = Appointment.objects.filter(doctor=doctor, status='ACCEPTED')
    return render(request, 'accepted_requests.html', {'appointments': accepted_appointments})


@login_required(login_url='/doctor/login/')
def doctor_canceled_appointments(request):
    doctor = get_object_or_404(models.Doctor, user=request.user)
    # Filter accepted appointments for this doctor
    canceled_appointments = Appointment.objects.filter(doctor=doctor, status='CANCELED')
    return render(request, 'doctor_canceled_appointments.html', {'canceled_appointments': canceled_appointments})


@login_required(login_url='/doctor/login/')
def manage_availability(request):
    doctor = get_object_or_404(models.Doctor, user=request.user)
    return render(request, 'manage_availability.html', {'doctor': doctor})


@login_required(login_url='/doctor/login/')
def delete_availability(request, availability_id):
    availability = get_object_or_404(models.Availability, id=availability_id)
    
    # Ensure the logged-in user is the owner of the availability
    doctor = get_object_or_404(models.Doctor, user=request.user)
    if availability.doctor == doctor:
        availability.delete()  # Delete the availability slot
    
    return redirect('manage_availability')  # Redirect to the manage availability page



@login_required(login_url='/doctor/login/')
def doctor_logout(request):
    logout(request)
    return redirect('doctor_login')