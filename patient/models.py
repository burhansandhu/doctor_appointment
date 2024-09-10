from django.db import models
from django.contrib.auth.models import User
from doctor.models import Doctor

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    phone = models.CharField(max_length=15)
    address = models.TextField()
    image = models.ImageField()


    def __str__(self):
        return self.user.username
    
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('CANCELED', 'Canceled'), 
        ('RESCHEDULED', 'Rescheduled'), 
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    #rescheduled_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Appointment with {self.doctor.user.username} on {self.appointment_date}"
