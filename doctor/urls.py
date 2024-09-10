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
from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('',views.doctor_signup,name='doctor_signup'),
    path('login/',views.doctor_login,name='doctor_login'),
    path('dashboard/',views.doctor_dashboard,name='doctor_dashboard'),
    path('update/',views.update_doctor_profile,name='update_doctor_profile'),
    path('pending_requests/',views.pending_requests,name='pending_requests'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('doctor_cancel_appointment/<int:appointment_id>/', views.doctor_cancel_appointment, name='doctor_cancel_appointment'),
    path('accepted_requests/',views.accepted_requests_view, name='accepted_requests'),
    path('canceled_requests/',views.doctor_canceled_appointments,name='doctor_canceled_appointment'),
    path('manage_availability/', views.manage_availability, name='manage_availability'),
    path('delete_availability/<int:availability_id>/', views.delete_availability, name='delete_availability'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='Reset_Password.html'), name='doctor_password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='Password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='Passowrd_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='Password_reset_complete.html'), name='password_reset_complete'),
    path('logout/',views.doctor_logout,name='doctor_logout'),
]
