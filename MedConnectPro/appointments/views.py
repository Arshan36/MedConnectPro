from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment
from .forms import AppointmentForm
from doctors.models import DoctorProfile, Availability
from patients.models import PatientProfile

@login_required
def book_appointment(request, doctor_id):
    """View for booking an appointment with a doctor"""
    if not request.user.is_patient():
        messages.error(request, 'Only patients can book appointments.')
        return redirect('home')
    
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    patient = get_object_or_404(PatientProfile, user=request.user)
    
    if request.method == 'POST':
        form = AppointmentForm(doctor, request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = patient
            
            # Calculate end time (assume 30 minute appointments)
            start_time = form.cleaned_data['start_time']
            hours, minutes = start_time.hour, start_time.minute
            end_time = datetime.strptime(f"{hours}:{minutes}", "%H:%M") + timedelta(minutes=30)
            appointment.end_time = end_time.time()
            
            appointment.save()
            
            messages.success(request, f'Appointment requested with Dr. {doctor.user.last_name} for {appointment.appointment_date}.')
            return redirect('appointment_list')
    else:
        form = AppointmentForm(doctor)
    
    context = {
        'form': form,
        'doctor': doctor,
    }
    return render(request, 'appointments/create.html', context)

@login_required
def appointment_list(request):
    """View for listing all appointments for the current user"""
    if request.user.is_doctor():
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        upcoming_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__gte=timezone.now().date()
        ).exclude(status='canceled').order_by('appointment_date', 'start_time')
        
        past_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date__lt=timezone.now().date()
        ).order_by('-appointment_date', '-start_time')
        
    elif request.user.is_patient():
        patient = get_object_or_404(PatientProfile, user=request.user)
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date__gte=timezone.now().date()
        ).exclude(status='canceled').order_by('appointment_date', 'start_time')
        
        past_appointments = Appointment.objects.filter(
            patient=patient,
            appointment_date__lt=timezone.now().date()
        ).order_by('-appointment_date', '-start_time')
    
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    return render(request, 'appointments/list.html', context)

@login_required
def appointment_detail(request, appointment_id):
    """View for viewing appointment details"""
    if request.user.is_doctor():
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    elif request.user.is_patient():
        appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/detail.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """View for canceling an appointment"""
    if request.user.is_doctor():
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    elif request.user.is_patient():
        appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')
    
    if not appointment.can_cancel():
        messages.error(request, 'This appointment cannot be canceled (less than 24 hours notice or already completed).')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        appointment.status = 'canceled'
        appointment.save()
        
        # Notify the other party
        if request.user.is_doctor():
            # Notify patient
            pass
        else:
            # Notify doctor
            pass
        
        messages.success(request, 'Appointment has been canceled successfully.')
        return redirect('appointment_list')
    
    return render(request, 'appointments/confirm_cancel.html', {'appointment': appointment})

@login_required
def confirm_appointment(request, appointment_id):
    """View for confirming a pending appointment (doctor only)"""
    if not request.user.is_doctor():
        messages.error(request, 'Only doctors can confirm appointments.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user, status='pending')
    
    if request.method == 'POST':
        appointment.status = 'confirmed'
        appointment.save()
        
        # Notify patient
        
        messages.success(request, 'Appointment has been confirmed successfully.')
        return redirect('appointment_list')
    
    return render(request, 'appointments/confirm_confirmation.html', {'appointment': appointment})

@login_required
def complete_appointment(request, appointment_id):
    """View for marking an appointment as completed (doctor only)"""
    if not request.user.is_doctor():
        messages.error(request, 'Only doctors can mark appointments as completed.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    
    if appointment.status not in ['confirmed', 'pending']:
        messages.error(request, 'Only confirmed or pending appointments can be marked as completed.')
        return redirect('appointment_detail', appointment_id=appointment_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        appointment.notes = notes
        appointment.status = 'completed'
        appointment.save()
        
        messages.success(request, 'Appointment has been marked as completed.')
        return redirect('appointment_list')
    
    return render(request, 'appointments/complete_appointment.html', {'appointment': appointment})

@login_required
def get_available_slots(request):
    """AJAX view for getting available time slots for a doctor on a specific date"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in'}, status=403)
    
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    try:
        doctor = DoctorProfile.objects.get(id=doctor_id)
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_of_week = selected_date.weekday()  # 0 = Monday, 6 = Sunday
        
        # Get doctor's availability for this day
        availabilities = Availability.objects.filter(doctor=doctor, day_of_week=day_of_week)
        
        if not availabilities:
            return JsonResponse({'slots': [], 'message': 'No availability on this day'})
        
        # Get existing appointments for this doctor on this date
        existing_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=selected_date,
            status__in=['pending', 'confirmed']
        ).values_list('start_time', flat=True)
        
        # Generate available time slots (30 minute intervals)
        available_slots = []
        
        for availability in availabilities:
            current_time = availability.start_time
            end_time = availability.end_time
            
            while current_time < end_time:
                if current_time not in existing_appointments:
                    # Format time as 12-hour clock string (e.g., "9:30 AM")
                    time_str = current_time.strftime('%I:%M %p').lstrip('0')
                    value_str = current_time.strftime('%H:%M')
                    available_slots.append({
                        'value': value_str,
                        'text': time_str
                    })
                
                # Add 30 minutes for next slot
                hours, minutes = current_time.hour, current_time.minute
                new_time = datetime.strptime(f"{hours}:{minutes}", "%H:%M") + timedelta(minutes=30)
                current_time = new_time.time()
        
        return JsonResponse({'slots': available_slots})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
