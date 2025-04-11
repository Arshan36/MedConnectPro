from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation, name='conversation'),
    path('start/<str:user_type>/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('api/mark-read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
]
