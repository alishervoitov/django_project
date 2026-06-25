from django.urls import path
from . import views

urlpatterns = [
    path('terminal/', views.check_id_attendance, name='check_id_page'),
]