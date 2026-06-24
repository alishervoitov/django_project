from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICE = (
        'teacher', 'O\'qituvchi',
        'student', 'Talaba',
        'staff', 'Xodim',
    )

    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICE,
        default='staff',
        help_text="Userning tizimdagi roli"
    )

    work_start_time = models.TimeField(
        default="08:30:00",
        help_text="Ushbu xodim yoki talaba kelishi kerak bo'lgan eng kech vaqt"
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    class Attendance(models.Model):

        STATUS_CHOICES = (
            ('on_time', 'Vaqtida keldi'),
            ('late', 'Kechikdi'),
            ('absent', 'Kelmagan'),
        )

        user = models.ForeignKey(
            CustomUser,
            on_delete=models.CASCADE,
            related_name='attendances'
        )

        date = models.DateField(
            auto_now_add=True,
            help_text="Davomat olingan kun"
        )

        check_in = models.TimeField(
            null=True,
            blank=True,
            help_text="Kelgan vaqti (Skaner birinchi marta bosilganda)"
        )

        check_out = models.TimeField(
            null=True,
            blank=True,
            help_text="Chiqib ketgan vaqti (Skaner ikkinchi marta bosilganda)"
        )

        status = models.CharField(
            max_length=10,
            choices=STATUS_CHOICES,
            default='absent'
        )

        delay_minutes = models.IntegerField(
            default=0,
            help_text="Necha daqiqa kechikib kelgani"
        )

        class Meta:
            unique_together = ('user', 'date')

        def __str__(self):
            return f"{self.user.username} - {self.date} ({self.get_status_display()})"

