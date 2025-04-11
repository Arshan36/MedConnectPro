from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_doctors, name='search_doctors'),
    path('ajax/', views.ajax_search_doctors, name='ajax_search_doctors'),
]
