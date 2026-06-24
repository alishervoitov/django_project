from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DailySchedule, Attendance


class CustomUserAdmin(UserAdmin):
    # Admin panel ro'yxatida ko'rinadigan ustunlar
    list_display = ('username', 'first_name', 'last_name', 'role', 'default_hours', 'is_staff')

    # Odam qo'shish va tahrirlash oynasidagi maydonlar guruhlari
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha Ma\'lumotlar', {'fields': ('role', 'default_hours')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Qo\'shimcha Ma\'lumotlar', {'fields': ('first_name', 'last_name', 'role', 'default_hours')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DailySchedule)
admin.site.register(Attendance)
