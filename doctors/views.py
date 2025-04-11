from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import DoctorProfile, Specialty
from .forms import DoctorProfileForm, AvailabilityFormSet
from appointments.models import Appointment

def doctor_profile(request, slug):
    """View for displaying a doctor's public profile"""
    doctor = get_object_or_404(DoctorProfile, slug=slug)
    context = {
        'doctor': doctor,
        'availability': doctor.get_availability(),
    }
    return render(request, 'doctors/profile.html', context)

@login_required
def doctor_dashboard(request):
    """Dashboard view for doctors"""
    if not request.user.is_doctor():
        messages.error(request, 'You do not have permission to access the doctor dashboard.')
        return redirect('home')
    
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor,
        status__in=['scheduled', 'confirmed'],
        appointment_date__gte=timezone.now().date()
    ).order_by('appointment_date', 'start_time')
    
    # Get pending appointment requests
    pending_appointments = Appointment.objects.filter(
        doctor=doctor,
        status='pending'
    ).order_by('created_at')
    
    # Check if profile is complete
    if not doctor.is_profile_complete():
        messages.warning(request, 'Please complete your profile to be visible to patients.')
    
    context = {
        'doctor': doctor,
        'upcoming_appointments': upcoming_appointments,
        'pending_appointments': pending_appointments,
        'profile_complete': doctor.is_profile_complete(),
    }
    return render(request, 'doctors/dashboard.html', context)

@login_required
def edit_doctor_profile(request):
    """View for editing doctor profile"""
    if not request.user.is_doctor():
        messages.error(request, 'You do not have permission to edit a doctor profile.')
        return redirect('home')
    
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('doctor_dashboard')
    else:
        form = DoctorProfileForm(instance=doctor)
    
    return render(request, 'doctors/edit_profile.html', {'form': form})

@login_required
def manage_availability(request):
    """View for managing doctor availability"""
    if not request.user.is_doctor():
        messages.error(request, 'You do not have permission to manage availability.')
        return redirect('home')
    
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    
    if request.method == 'POST':
        formset = AvailabilityFormSet(request.POST, instance=doctor)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Your availability has been updated successfully.')
            return redirect('doctor_dashboard')
    else:
        formset = AvailabilityFormSet(instance=doctor)
    
    return render(request, 'doctors/manage_availability.html', {'formset': formset})

def search_doctors(request):
    """View for searching doctors"""
    specialties = Specialty.objects.all()
    
    specialty_id = request.GET.get('specialty', '')
    location = request.GET.get('location', '')
    name = request.GET.get('name', '')
    
    doctors = DoctorProfile.objects.all()
    
    if specialty_id and specialty_id.isdigit():
        doctors = doctors.filter(specialty_id=specialty_id)
    
    if location:
        doctors = doctors.filter(
            Q(clinic_city__icontains=location) | 
            Q(clinic_state__icontains=location) |
            Q(clinic_zip__icontains=location)
        )
    
    if name:
        doctors = doctors.filter(
            Q(user__first_name__icontains=name) | 
            Q(user__last_name__icontains=name)
        )
    
    context = {
        'doctors': doctors,
        'specialties': specialties,
        'selected_specialty': specialty_id,
        'location': location,
        'name': name,
    }
    return render(request, 'search/search.html', context)

def ajax_search_doctors(request):
    """AJAX view for searching doctors dynamically"""
    specialty_id = request.GET.get('specialty', '')
    location = request.GET.get('location', '')
    name = request.GET.get('name', '')
    
    doctors = DoctorProfile.objects.all()
    
    if specialty_id and specialty_id.isdigit():
        doctors = doctors.filter(specialty_id=specialty_id)
    
    if location:
        doctors = doctors.filter(
            Q(clinic_city__icontains=location) | 
            Q(clinic_state__icontains=location) |
            Q(clinic_zip__icontains=location)
        )
    
    if name:
        doctors = doctors.filter(
            Q(user__first_name__icontains=name) | 
            Q(user__last_name__icontains=name)
        )
    
    results = []
    for doctor in doctors:
        results.append({
            'id': doctor.id,
            'name': doctor.get_full_name(),
            'specialty': doctor.specialty.name if doctor.specialty else '',
            'location': f"{doctor.clinic_city}, {doctor.clinic_state}",
            'years_experience': doctor.years_of_experience,
            'profile_url': f"/doctors/profile/{doctor.slug}/",
        })
    
    return JsonResponse(results, safe=False)
