from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, DailySchedule, Attendance
from datetime import datetime


def check_id_attendance(request):
    if request.method == "POST":
        input_id = request.POST.get('staff_id', '').strip()

        try:
            user = CustomUser.objects.get(staff_id=input_id)
        except CustomUser.DoesNotExist:
            messages.error(request, f" Tizimda bunday ID mavjud emas: {input_id}")
            return redirect('check_id_page')

        today = timezone.now().date()
        current_time = timezone.now().time()
        current_weekday = today.weekday()  # 0=Dushanba, ..., 6=Yakshanba

        schedule = DailySchedule.objects.filter(user=user, day_of_week=current_weekday).first()

        if not schedule or schedule.expected_hours == 0:
            messages.error(request, f" {user.get_full_name()} uchun bugun dam kuni yoki grafik belgilanmagan!")
            return redirect('check_id_page')

        expected_minutes = schedule.expected_hours * 60

        attendance, created = Attendance.objects.get_or_create(
            user=user,
            date=today,
            defaults={'check_in': current_time}
        )

        if created:

            scheduled_start = datetime.combine(today, schedule.start_time)
            actual_arrival = datetime.combine(today, current_time)

            if actual_arrival > scheduled_start:
                late_min = int((actual_arrival - scheduled_start).total_seconds() / 60)
                attendance.late_minutes = late_min
                attendance.save()

                messages.warning(
                    request,
                    f"⚠ {user.get_full_name()} siz ishga {late_min} daqiqa KECHIKDINGIZ! "
                    f"Grafik: {schedule.start_time.strftime('%H:%M')}, Kelgan vaqtingiz: {current_time.strftime('%H:%M:%S')}"
                )
            else:

                messages.success(
                    request,
                    f" Xush kelibsiz, {user.get_full_name()}! Ishga o'z vaqtida keldingiz. "
                    f"Kelgan vaqtingiz: {current_time.strftime('%H:%M:%S')}. Bugungi rejangiz: {schedule.expected_hours} soat."
                )
        else:

            attendance.check_out = current_time
            dt_in = datetime.combine(today, attendance.check_in)
            dt_out = datetime.combine(today, current_time)
            minutes_spent = int((dt_out - dt_in).total_seconds() / 60)
            attendance.minutes_spent = minutes_spent

            scheduled_start = datetime.combine(today, schedule.start_time)
            scheduled_leave = scheduled_start + timezone.timedelta(minutes=expected_minutes)

            if dt_out < scheduled_leave:
                early_min = int((scheduled_leave - dt_out).total_seconds() / 60)
                attendance.early_out_minutes = early_min
                attendance.save()

                messages.warning(
                    request,
                    f" Xayr, {user.get_full_name()}! Siz ish vaqti tugashidan {early_min} daqiqa OLDIN (ERTA) ketyapsiz! "
                    f"Jami ishlagan vaqtingiz: {minutes_spent} daqiqa."
                )
            else:
                attendance.save()
                messages.success(
                    request,
                    f" Xayr, {user.get_full_name()}! Kunlik ish rejangiz muvaffaqiyatli yakunlandi.  "
                    f"Jami sarflangan vaqt: {minutes_spent} daqiqa."
                )

        return redirect('check_id_page')

    return render(request, 'attendance/check_id.html')
