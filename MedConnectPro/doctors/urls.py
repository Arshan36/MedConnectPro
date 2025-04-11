from django.urls import path
from . import views

urlpatterns = [
    path('profile/<slug:slug>/', views.doctor_profile, name='doctor_profile'),
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('profile/edit/', views.edit_doctor_profile, name='edit_doctor_profile'),
    path('availability/manage/', views.manage_availability, name='manage_availability'),
]
