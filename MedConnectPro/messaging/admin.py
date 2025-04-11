from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'content', 'created_at')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient', 'created_at', 'updated_at')
    search_fields = (
        'doctor__user__first_name', 'doctor__user__last_name',
        'patient__user__first_name', 'patient__user__last_name'
    )
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('conversation__doctor__user__email', 'conversation__patient__user__email', 'content')
    readonly_fields = ('created_at',)
