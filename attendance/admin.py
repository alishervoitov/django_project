from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# DIQQAT: Ranglar va vizual ko'rinish ishlashi uchun shu import shart:
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import CustomUser, DailySchedule, Attendance

# 1. YANGI ODAM QO'ShISh UChUN TOZA FORMA (Username va Parolsiz)
class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'staff_id', 'role', 'default_hours')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

# 2. USER MODELI SOZLAMALARI
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('staff_id', 'first_name', 'last_name', 'role', 'default_hours', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    ordering = ('staff_id',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'staff_id', 'role', 'default_hours'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('staff_id',)}),
        ('Shaxsiy Ma\'lumotlar', {'fields': ('first_name', 'last_name', 'email')}),
        ('Qo\'shimcha Ma\'lumotlar', {'fields': ('role', 'default_hours')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

# 3. DAVOMAT (ATTENDANCE) MODELI SOZLAMALARI (SOAT VA DAQIQADA)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'check_in', 'check_out', 'formatted_time_spent', 'status_late', 'status_early')
    list_filter = ('date', 'user__role', 'user')
    search_fields = ('user__first_name', 'user__last_name', 'user__staff_id')

    def _format_minutes(self, total_minutes):
        if not total_minutes or total_minutes == 0:
            return "0 d"
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if hours > 0:
            return f"{hours} soat {minutes} daqiqa"
        return f"{minutes} daqiqa"

    def formatted_time_spent(self, obj):
        return self._format_minutes(obj.minutes_spent)
    formatted_time_spent.short_description = "Ishlagan vaqti"

    # TO'G'RILANGAN KECHIKISH USTUNI
    def status_late(self, obj):
        if obj.late_minutes > 0:
            readable_time = self._format_minutes(obj.late_minutes)
            # format_html ichiga {} qo'yib, argument sifatida qiymat beramiz
            return format_html('<span style="color: red; font-weight: bold;">🚨 {} kechikdi</span>', readable_time)
        # O'zgaruvchisiz static HTML uchun mark_safe ishlatamiz
        return mark_safe('<span style="color: green;">✔ Vaqtida</span>')
    status_late.short_description = "Kechikish holati"

    # TO'G'RILANGAN ERTA KETISH USTUNI
    def status_early(self, obj):
        if obj.early_out_minutes > 0:
            readable_time = self._format_minutes(obj.early_out_minutes)
            return format_html('<span style="color: orange; font-weight: bold;">🏃‍♂️ {} vaqtli ketdi</span>', readable_time)
        return mark_safe('<span style="color: green;">✔ To\'liq ishladi</span>')
    status_early.short_description = "Erta ketish holati"


# 4. ESKI REGISTRATSIYALARNI TOZALAB, QAYTADAN RO'YXATGA OLISH
admin.site.unregister(CustomUser) if admin.site.is_registered(CustomUser) else None
admin.site.register(CustomUser, CustomUserAdmin)

admin.site.unregister(DailySchedule) if admin.site.is_registered(DailySchedule) else None
admin.site.register(DailySchedule)

admin.site.unregister(Attendance) if admin.site.is_registered(Attendance) else None
admin.site.register(Attendance, AttendanceAdmin)  # AttendanceAdmin ulandi!
