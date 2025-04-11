from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q
from .models import Conversation, Message
from doctors.models import DoctorProfile
from patients.models import PatientProfile

@login_required
def inbox(request):
    """View for displaying a user's message inbox"""
    user = request.user
    
    if user.is_doctor():
        doctor = get_object_or_404(DoctorProfile, user=user)
        conversations = Conversation.objects.filter(doctor=doctor).order_by('-updated_at')
    elif user.is_patient():
        patient = get_object_or_404(PatientProfile, user=user)
        conversations = Conversation.objects.filter(patient=patient).order_by('-updated_at')
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')
    
    # Add unread message count to each conversation
    for conv in conversations:
        conv.unread_count = conv.get_unread_count(user)
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def conversation(request, conversation_id):
    """View for displaying and handling a specific conversation"""
    user = request.user
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check permissions
    if user.is_doctor() and conversation.doctor.user != user:
        return HttpResponseForbidden("You don't have permission to view this conversation")
    
    if user.is_patient() and conversation.patient.user != user:
        return HttpResponseForbidden("You don't have permission to view this conversation")
    
    # Mark unread messages from the other user as read
    if user.is_doctor():
        Message.objects.filter(
            conversation=conversation,
            sender=conversation.patient.user,
            is_read=False
        ).update(is_read=True)
    else:
        Message.objects.filter(
            conversation=conversation,
            sender=conversation.doctor.user,
            is_read=False
        ).update(is_read=True)
    
    # Get messages for this conversation
    messages_list = conversation.messages.order_by('created_at')
    
    context = {
        'conversation': conversation,
        'messages': messages_list,
    }
    return render(request, 'messaging/conversation.html', context)

@login_required
def start_conversation(request, user_type, user_id):
    """View for starting a new conversation with a doctor or patient"""
    current_user = request.user
    
    if user_type == 'doctor':
        if current_user.is_doctor():
            messages.error(request, 'Doctors cannot start conversations with other doctors.')
            return redirect('inbox')
        
        doctor = get_object_or_404(DoctorProfile, id=user_id)
        patient = get_object_or_404(PatientProfile, user=current_user)
        
        # Check if conversation already exists
        conversation, created = Conversation.objects.get_or_create(
            doctor=doctor,
            patient=patient
        )
    
    elif user_type == 'patient':
        if current_user.is_patient():
            messages.error(request, 'Patients cannot start conversations with other patients.')
            return redirect('inbox')
        
        doctor = get_object_or_404(DoctorProfile, user=current_user)
        patient = get_object_or_404(PatientProfile, id=user_id)
        
        # Check if conversation already exists
        conversation, created = Conversation.objects.get_or_create(
            doctor=doctor,
            patient=patient
        )
    
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('inbox')
    
    return redirect('conversation', conversation_id=conversation.id)

@login_required
def mark_message_read(request, message_id):
    """AJAX view for marking a message as read"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check permissions
    user = request.user
    conversation = message.conversation
    
    if user.is_doctor() and conversation.doctor.user != user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if user.is_patient() and conversation.patient.user != user:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Only mark as read if current user is not the sender
    if message.sender != user and not message.is_read:
        message.mark_as_read()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
