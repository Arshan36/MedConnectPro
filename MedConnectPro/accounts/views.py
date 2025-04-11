from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import DoctorSignUpForm, PatientSignUpForm
from doctors.models import DoctorProfile
from patients.models import PatientProfile

def signup_view(request):
    """View for selecting user type during sign up"""
    return render(request, 'accounts/signup.html')

def doctor_signup(request):
    """View for doctor sign up"""
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create an empty doctor profile
            DoctorProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
    else:
        form = DoctorSignUpForm()
    return render(request, 'accounts/signup_doctor.html', {'form': form})

def patient_signup(request):
    """View for patient sign up"""
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create an empty patient profile
            PatientProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
    else:
        form = PatientSignUpForm()
    return render(request, 'accounts/signup_patient.html', {'form': form})

@login_required
def dashboard(request):
    """Main dashboard view that redirects to appropriate user dashboard"""
    if request.user.is_doctor():
        return redirect('doctor_dashboard')
    elif request.user.is_patient():
        return redirect('patient_dashboard')
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')
