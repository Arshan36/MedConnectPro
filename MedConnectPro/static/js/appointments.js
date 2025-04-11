// JavaScript for appointment booking and management

document.addEventListener('DOMContentLoaded', function() {
    const appointmentDateInput = document.getElementById('id_appointment_date');
    const appointmentTimeSelect = document.getElementById('id_start_time');
    const doctorIdInput = document.getElementById('doctor_id');
    
    // Function to fetch available time slots for a doctor on a specific date
    function fetchAvailableSlots() {
        if (!appointmentDateInput || !appointmentTimeSelect || !doctorIdInput) {
            return;
        }
        
        const date = appointmentDateInput.value;
        const doctorId = doctorIdInput.value;
        
        if (!date || !doctorId) {
            return;
        }
        
        // Clear current options
        appointmentTimeSelect.innerHTML = '<option value="">Loading available times...</option>';
        appointmentTimeSelect.disabled = true;
        
        // Fetch available slots
        fetch(`/appointments/get-available-slots/?doctor_id=${doctorId}&date=${date}`)
            .then(response => response.json())
            .then(data => {
                appointmentTimeSelect.innerHTML = '';
                
                if (data.error) {
                    appointmentTimeSelect.innerHTML = '<option value="">Error loading times</option>';
                    console.error(data.error);
                    return;
                }
                
                if (!data.slots || data.slots.length === 0) {
                    appointmentTimeSelect.innerHTML = '<option value="">No available times on this date</option>';
                    return;
                }
                
                // Add default option
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = 'Select a time';
                appointmentTimeSelect.appendChild(defaultOption);
                
                // Add time slot options
                data.slots.forEach(slot => {
                    const option = document.createElement('option');
                    option.value = slot.value;
                    option.textContent = slot.text;
                    appointmentTimeSelect.appendChild(option);
                });
                
                appointmentTimeSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error fetching available slots:', error);
                appointmentTimeSelect.innerHTML = '<option value="">Error loading times</option>';
                appointmentTimeSelect.disabled = false;
            });
    }
    
    // Set up event listener for date input
    if (appointmentDateInput) {
        appointmentDateInput.addEventListener('change', fetchAvailableSlots);
        
        // If date is already selected (e.g., when returning to form with errors), fetch slots
        if (appointmentDateInput.value) {
            fetchAvailableSlots();
        }
    }
    
    // Appointment cancellation confirmation
    const cancelButtons = document.querySelectorAll('.cancel-appointment-btn');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to cancel this appointment? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Appointment confirmation
    const confirmButtons = document.querySelectorAll('.confirm-appointment-btn');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to confirm this appointment?')) {
                e.preventDefault();
            }
        });
    });
    
    // Appointment completion
    const completeButtons = document.querySelectorAll('.complete-appointment-btn');
    completeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to mark this appointment as completed?')) {
                e.preventDefault();
            }
        });
    });
    
    // Filtering appointments
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const status = this.value;
            const appointments = document.querySelectorAll('.appointment-item');
            
            appointments.forEach(appointment => {
                if (status === 'all' || appointment.getAttribute('data-status') === status) {
                    appointment.style.display = 'block';
                } else {
                    appointment.style.display = 'none';
                }
            });
        });
    }
});
