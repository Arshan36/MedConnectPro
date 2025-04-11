from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import PatientProfile, MedicalDocument
from .forms import PatientProfileForm, MedicalDocumentForm
from appointments.models import Appointment
from django.utils import timezone

@login_required
def patient_profile(request, slug):
    """View for displaying a patient's profile"""
    # Only allow viewing of own profile or doctors who have appointments with the patient
    patient = get_object_or_404(PatientProfile, slug=slug)
    
    if request.user.is_patient() and request.user != patient.user:
        return HttpResponseForbidden("You don't have permission to view this profile")
    
    if request.user.is_doctor():
        # Check if the doctor has any appointments with this patient
        doctor = request.user.doctor_profile
        has_appointment = Appointment.objects.filter(
            doctor=doctor, 
            patient=patient,
            status__in=['confirmed', 'completed']
        ).exists()
        
        if not has_appointment:
            return HttpResponseForbidden("You don't have permission to view this profile")
    
    context = {
        'patient': patient,
    }
    return render(request, 'patients/profile.html', context)

@login_required
def patient_dashboard(request):
    """Dashboard view for patients"""
    if not request.user.is_patient():
        messages.error(request, 'You do not have permission to access the patient dashboard.')
        return redirect('home')
    
    patient = get_object_or_404(PatientProfile, user=request.user)
    
    # Get upcoming appointments
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        status__in=['scheduled', 'confirmed'],
        appointment_date__gte=timezone.now().date()
    ).order_by('appointment_date', 'start_time')
    
    # Get past appointments
    past_appointments = Appointment.objects.filter(
        patient=patient,
        status='completed'
    ).order_by('-appointment_date', '-start_time')
    
    # Check if profile is complete
    if not patient.is_profile_complete():
        messages.warning(request, 'Please complete your profile for a better experience.')
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'profile_complete': patient.is_profile_complete(),
    }
    return render(request, 'patients/dashboard.html', context)

@login_required
def edit_patient_profile(request):
    """View for editing patient profile"""
    if not request.user.is_patient():
        messages.error(request, 'You do not have permission to edit a patient profile.')
        return redirect('home')
    
    patient = get_object_or_404(PatientProfile, user=request.user)
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('patient_dashboard')
    else:
        form = PatientProfileForm(instance=patient)
    
    return render(request, 'patients/edit_profile.html', {'form': form})

@login_required
def medical_documents(request):
    """View for listing patient's medical documents"""
    if not request.user.is_patient():
        messages.error(request, 'You do not have permission to access medical documents.')
        return redirect('home')
    
    patient = get_object_or_404(PatientProfile, user=request.user)
    documents = MedicalDocument.objects.filter(patient=patient).order_by('-uploaded_at')
    
    context = {
        'patient': patient,
        'documents': documents,
    }
    return render(request, 'patients/medical_documents.html', context)

@login_required
def upload_document(request):
    """View for uploading a medical document"""
    if not request.user.is_patient():
        messages.error(request, 'You do not have permission to upload medical documents.')
        return redirect('home')
    
    patient = get_object_or_404(PatientProfile, user=request.user)
    
    if request.method == 'POST':
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.save()
            messages.success(request, 'Your document has been uploaded successfully.')
            return redirect('medical_documents')
    else:
        form = MedicalDocumentForm()
    
    return render(request, 'patients/upload_document.html', {'form': form})

@login_required
def delete_document(request, document_id):
    """View for deleting a medical document"""
    if not request.user.is_patient():
        messages.error(request, 'You do not have permission to delete medical documents.')
        return redirect('home')
    
    document = get_object_or_404(MedicalDocument, id=document_id, patient__user=request.user)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Your document has been deleted successfully.')
        return redirect('medical_documents')
    
    return render(request, 'patients/confirm_delete_document.html', {'document': document})
