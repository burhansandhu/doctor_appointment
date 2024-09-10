"""
URL configuration for doctorAppointment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetView

urlpatterns = [
        path('Psignup/',views.patient_signup,name='patient_signup'),
        path('Plogin/',views.patient_login,name='patient_login'),
        path('Pdashboard/',views.patient_dashboard,name='patient_dashboard'),
        path('appointment_request/',views.request_appointment,name='appointment_request'),
        path('Pupadte/',views.patient_update,name='patient_update'),
        path('doctor_availability/',views.doctor_availability,name='doctor_availability'),
        path('view_requests/',views.view_requests,name='view_requests'),
        path('patient_cancel_appointment/<int:appointment_id>/', views.patient_cancel_appointment, name='patient_cancel_appointment'),
        path('password_reset/', auth_views.PasswordResetView.as_view(template_name='Reset_Password.html'), name='patient_password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='Password_reset_done.html'), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='Passowrd_reset_confirm.html'), name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='Password_reset_complete.html'), name='password_reset_complete'),
        path('search_doctor/',views.search_doctor,name='search_doctor'),
        path('Plogout/',views.patient_logout,name='patient_logout'),
]

