from django.urls import path
from . import views

urlpatterns = [
    path('profile/<slug:slug>/', views.patient_profile, name='patient_profile'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('profile/edit/', views.edit_patient_profile, name='edit_patient_profile'),
    path('documents/', views.medical_documents, name='medical_documents'),
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/delete/<int:document_id>/', views.delete_document, name='delete_document'),
]
