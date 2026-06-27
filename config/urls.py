from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_admin_automatically(request):
    User = get_user_model()
    if not User.objects.filter(staff_id="admin").exists():
        User.objects.create_superuser(
            staff_id="AB882002",
            first_name="Alisher",
            last_name="Voitov",
            password="alisher",
            email="admin@example.com"
        )
        return HttpResponse("Admin akkaunt muvaffaqiyatli yaratildi! Endi bu urlni ochirib tashlasangiz bo'ladi.")
    return HttpResponse("Admin akkaunt allaqachon mavjud.")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('make-admin', create_admin_automatically),
    path('', include('attendance.urls')),
]

