from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, staff_id, first_name, last_name, password=None, **extra_fields):
        if not staff_id:
            raise ValueError("ID raqami (Karta/Guvohnoma) kiritilishi shart!")

        extra_fields.setdefault('is_active', True)

        user = self.model(
            staff_id=staff_id,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        if not password:
            password = staff_id

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, staff_id, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuserda is_staff=True bo\'lishi shart.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuserda is_superuser=True bo\'lishi shart.')

        return self.create_user(staff_id, first_name, last_name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('teacher', "O'qituvchi"),
        ('student', "Talaba"),
        ('staff', "Xodim"),
    ]

    staff_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="ID raqami (Karta/Guvohnoma)"
    )
    first_name = models.CharField(max_length=150, verbose_name="Ismi")
    last_name = models.CharField(max_length=150, verbose_name="Familiyasi")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff', verbose_name="Roli")
    default_hours = models.PositiveIntegerField(default=8, verbose_name="Standart kunlik ish soati")

    is_active = models.BooleanField(default=True, verbose_name="Faol")
    is_staff = models.BooleanField(default=False, verbose_name="Admin panelga kira oladi")
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'staff_id'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return f"{self.staff_id} - {self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

class DailySchedule(models.Model):
    WEEKDAYS = [
        (0, 'Dushanba'), (1, 'Seshanba'), (2, 'Chorshanba'),
        (3, 'Payshanba'), (4, 'Juma'), (5, 'Shanba'), (6, 'Yakshanba'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=WEEKDAYS, verbose_name="Hafta kuni")
    start_time = models.TimeField(verbose_name="Ish boshlanish vaqti", help_text="Masalan: 09:00")
    expected_hours = models.PositiveIntegerField(verbose_name="Ish vaqti (soat)", default=8)

    class Meta:
        unique_together = ('user', 'day_of_week')
        verbose_name = "Kunlik Grafik"
        verbose_name_plural = "Kunlik Grafiklar"


# 4. DAVOMAT MODELI
class Attendance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True, verbose_name="Sana")
    check_in = models.TimeField(auto_now_add=True, verbose_name="Kelgan vaqti")
    check_out = models.TimeField(null=True, blank=True, verbose_name="Ketgan vaqti")
    minutes_spent = models.PositiveIntegerField(default=0, verbose_name="Ishlagan vaqti (daqiqa)")
    late_minutes = models.PositiveIntegerField(default=0, verbose_name="Kechikish (daqiqa)")
    early_out_minutes = models.PositiveIntegerField(default=0, verbose_name="Erta ketish (daqiqa)")

    class Meta:
        verbose_name = "Davomat"
        verbose_name_plural = "Davomatlar"

    def __str__(self):
        return f"{self.user.get_full_name()} | {self.date}"