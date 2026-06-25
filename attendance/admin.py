from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, DailySchedule, Attendance


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'staff_id', 'role', 'default_hours')

    def save(self, commit=True):

        user = super().save(commit=False)
        if commit:
            user.save()
        return user


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


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'check_in', 'check_out', 'minutes_spent', 'status_late', 'status_early')
    list_filter = ('date', 'user__role', 'user')
    search_fields = ('user__first_name', 'user__last_name', 'user__staff_id')

    def status_late(self, obj):
        if obj.late_minutes > 0:
            return format_html('<span style="color: red; font-weight: bold;">🚨 {} daqiqa kechikdi</span>',
                               obj.late_minutes)
        return format_html('<span style="color: green;">✔ Vaqtida</span>')

    status_late.short_description = "Kechikish holati"

    def status_early(self, obj):
        if obj.early_out_minutes > 0:
            return format_html('<span style="color: orange; font-weight: bold;">🏃‍♂️ {} daqiqa vaqtli ketdi</span>',
                               obj.early_out_minutes)
        return format_html('<span style="color: green;">✔ To\'liq ishladi</span>')

    status_early.short_description = "Erta ketish holati"


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DailySchedule)
admin.site.register(Attendance)
