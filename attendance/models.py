from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', "O'qituvchi"),
        ('student', "Talaba"),
        ('staff', "Xodim"),
    ]

    # Ism va Familiya AbstractUser ichida tayyor bor,
    # lekin majburiy qilish yoki boshqarish uchun bu yerda ham ko'rsatish mumkin:
    first_name = models.CharField(max_length=150, verbose_name="Ismi")
    last_name = models.CharField(max_length=150, verbose_name="Familiyasi")

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff',
        verbose_name="Roli"
    )
    default_hours = models.PositiveIntegerField(
        default=8,
        verbose_name="Standart kunlik ish soati"
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class DailySchedule(models.Model):
    WEEKDAYS = [
        (0, 'Dushanba'),
        (1, 'Seshanba'),
        (2, 'Chorshanba'),
        (3, 'Payshanba'),
        (4, 'Juma'),
        (5, 'Shanba'),
        (6, 'Yakshanba'),
    ]
    # Endi profillar yo'q, to'g'ridan-to'g'ri CustomUser'ga bog'laymiz
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=WEEKDAYS, verbose_name="Hafta kuni")
    expected_hours = models.PositiveIntegerField(verbose_name="Ushbu kundagi ish vaqti (soat)")

    class Meta:
        unique_together = ('user', 'day_of_week')


class Attendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    check_in = models.TimeField(auto_now_add=True)
    check_out = models.TimeField(null=True, blank=True)
    minutes_spent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.get_full_name()} | {self.date}"

