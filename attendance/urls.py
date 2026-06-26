from django.urls import path
from . import views

urlpatterns = [
    path('terminal/', views.check_id_attendance, name='check_id_page'),
    path('login/', views.login_page, name='login_page'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('monitoring/<int:user_id>/', views.user_monitoring, name='user_monitoring'),
    path('logout/', views.logout_page, name='logout_page'),
]