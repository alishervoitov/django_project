import calendar
from django.contrib.auth import logout, authenticate, login
from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import CustomUser, DailySchedule, Attendance
from datetime import datetime, timedelta
from django.contrib.auth.decorators import user_passes_test, login_required

def check_id_attendance(request):
    if request.method == "POST":
        input_id = request.POST.get('staff_id', '').strip()
        try:
            user = CustomUser.objects.get(staff_id=input_id, is_active=True)
        except CustomUser.DoesNotExist:
            messages.error(request, f" Tizimda bunday ID mavjud emas: {input_id}")
            return redirect('check_id_page')

        if timezone.is_aware(timezone.now()):
            local_now = timezone.localtime(timezone.now())
        else:
            local_now = datetime.now()

        today = local_now.date()
        current_time = local_now.time()
        current_weekday = today.weekday()

        schedule = DailySchedule.objects.filter(user=user, day_of_week=current_weekday).first()

        if not schedule or schedule.expected_hours == 0:
            messages.error(request, f" {user.get_full_name()} uchun bugun dam kuni yoki grafik belgilanmagan!")
            return redirect('check_id_page')

        expected_minutes = schedule.expected_hours * 60
        attendance = Attendance.objects.filter(user=user, date=today).first()

        if not attendance:
            scheduled_start = datetime.combine(today, schedule.start_time)
            actual_arrival = datetime.combine(today, current_time)
            late_min = 0
            if actual_arrival > scheduled_start:
                late_min = int((actual_arrival - scheduled_start).total_seconds() / 60)

            Attendance.objects.create(
                user=user,
                date=today,
                check_in=current_time,
                late_minutes=late_min,
                early_out_minutes=0,
                minutes_spent=0
            )

            if late_min > 0:
                messages.warning(request, f"⚠ {user.get_full_name()} siz ishga {late_min} daqiqa KECHIKDINGIZ!")
            else:
                messages.success(request, f" Xush kelibsiz, {user.get_full_name()}! Ishga o'z vaqtida keldingiz.")

        else:
            if attendance.check_out is not None:
                messages.warning(request, f"⚠ Siz bugun keldi-ketdi jarayonini yakunlagansiz!")
                return redirect('check_id_page')

            attendance.check_out = current_time

            dt_in = datetime.combine(today, attendance.check_in)
            dt_out = datetime.combine(today, current_time)

            minutes_spent = int((dt_out - dt_in).total_seconds() / 60)
            attendance.minutes_spent = minutes_spent

            scheduled_start = datetime.combine(today, schedule.start_time)
            scheduled_leave = scheduled_start + timezone.timedelta(minutes=expected_minutes)
            early_min = 0

            if dt_out < scheduled_leave:
                early_min = int((scheduled_leave - dt_out).total_seconds() / 60)
                attendance.early_out_minutes = early_min
            attendance.save()
            if early_min > 0:
                messages.warning(request,
                                 f" Xayr, {user.get_full_name()}! Ish vaqtidan {early_min} daqiqa OLDIN ketyapsiz!")
            else:
                messages.success(request, f" Xayr, {user.get_full_name()}! Kunlik ish rejangiz yakunlandi.")
        return redirect('check_id_page')
    return render(request, 'attendance/check_id.html')

def login_page(request):
    if request.method == 'POST':
        staff_id = request.POST.get('staff_id', '').strip()
        password = request.POST.get('password', '').strip()
        if not staff_id or not password:
            messages.error(request, "ID raqami va parolni to'liq kiriting!")
            return render(request, 'attendance/login.html')
        user = authenticate(request, username=staff_id, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Xush kelibsiz, {user.get_full_name()}!")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Sizda boshqaruv paneliga kirish huquqi yo'q!")
        else:
            messages.error(request, "ID raqami yoki parol noto'g'ri!")
    return render(request, 'attendance/login.html')


@login_required(login_url='login_page')
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Sizda ushbu sahifaga ruxsat yo'q!")
        return redirect('login_page')
    role_filter = request.GET.get('role', '').strip()
    weekday_filter = request.GET.get('weekday', '').strip()
    date_filter = request.GET.get('date', '').strip()

    attendances = Attendance.objects.all().select_related('user')

    if date_filter:
        attendances = attendances.filter(date=date_filter)
    elif weekday_filter == '' and role_filter == '':
        attendances = attendances.filter(date=timezone.now().date())
    if role_filter:
        attendances = attendances.filter(user__role=role_filter)
    if weekday_filter != '':
        django_weekday = (int(weekday_filter) + 1) % 7 + 1
        attendances = attendances.filter(date__weekday=django_weekday)

    attendances = attendances.order_by('-date', 'check_in')
    for att in attendances:
        def to_hours(minutes):
            if not minutes or minutes == 0:
                return "-"
            if minutes < 24 and att.check_out is not None:
                return f"{minutes} soat"
            h = int(minutes) // 60
            m = int(minutes) % 60
            return f"{h} soat {m} d" if h > 0 else f"{m} daqiqa"
        att.readable_spent = to_hours(att.minutes_spent)
        att.readable_late = to_hours(att.late_minutes) if att.late_minutes > 0 else "-"
        att.readable_early = to_hours(att.early_out_minutes) if att.early_out_minutes > 0 else "-"

    today = timezone.now().date()
    total_users = CustomUser.objects.filter(is_active=True).count()
    attended_today = Attendance.objects.filter(date=today).count()
    late_today = Attendance.objects.filter(date=today, late_minutes__gt=0).count()
    absent_today = max(0, total_users - attended_today)

    context = {
        'attendances': attendances,
        'total_users': total_users,
        'attended_today': attended_today,
        'late_today': late_today,
        'absent_today': absent_today,
        'current_role': role_filter,
        'current_weekday': weekday_filter,
        'current_date': date_filter or str(today),
    }
    return render(request, 'attendance/dashboard.html', context)


def logout_page(request):
    logout(request)
    messages.info(request, "Tizimdan muvaffaqiyatli chiqdingiz.")
    return redirect('login_page')


@login_required(login_url='login_page')
def user_monitoring(request, user_id):
    if not request.user.is_staff:
        messages.error(request, "Sizda ushbu sahifaga ruxsat yo'q!")
        return redirect('login_page')

    employee = get_object_or_404(CustomUser, id=user_id)

    if timezone.is_aware(timezone.now()):
        local_now = timezone.localtime(timezone.now())
    else:
        local_now = datetime.now()

    today = local_now.date()

    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    weekly_attendances = Attendance.objects.filter(
        user=employee,
        date__range=[start_of_week, end_of_week]
    ).order_by('date')

    weekly_stats = weekly_attendances.aggregate(
        days=Count('id'),
        minutes=Sum('minutes_spent'),
        late=Sum('late_minutes'),
        early=Sum('early_out_minutes')
    )

    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    _, last_day = calendar.monthrange(year, month)
    start_of_month = datetime(year, month, 1).date()
    end_of_month = datetime(year, month, last_day).date()

    monthly_attendances = Attendance.objects.filter(
        user=employee,
        date__range=[start_of_month, end_of_month]
    ).order_by('-date')

    monthly_stats = monthly_attendances.aggregate(
        days=Count('id'),
        minutes=Sum('minutes_spent'),
        late=Sum('late_minutes'),
        early=Sum('early_out_minutes')
    )

    def format_to_hours(minutes):
        if not minutes: return "0 soat"
        h = minutes // 60
        m = minutes % 60
        return f"{h} soat {m} d" if h > 0 else f"{m} daqiqa"

    w_stats = {
        'days': weekly_stats['days'] or 0,
        'work_hours': format_to_hours(weekly_stats['minutes']),
        'late': format_to_hours(weekly_stats['late']),
        'early': format_to_hours(weekly_stats['early']),
    }

    m_stats = {
        'days': monthly_stats['days'] or 0,
        'work_hours': format_to_hours(monthly_stats['minutes']),
        'late': format_to_hours(monthly_stats['late']),
        'early': format_to_hours(monthly_stats['early']),
    }

    for att in weekly_attendances:
        att.readable_spent = format_to_hours(att.minutes_spent)
        att.readable_late = format_to_hours(att.late_minutes) if att.late_minutes > 0 else None
        att.readable_early = format_to_hours(att.early_out_minutes) if att.early_out_minutes > 0 else None

    for att in monthly_attendances:
        att.readable_spent = format_to_hours(att.minutes_spent)
        att.readable_late = format_to_hours(att.late_minutes) if att.late_minutes > 0 else None
        att.readable_early = format_to_hours(att.early_out_minutes) if att.early_out_minutes > 0 else None

    months_list = [
        (1, "Yanvar"), (2, "Fevral"), (3, "Mart"), (4, "Aprel"), (5, "May"), (6, "Iyun"),
        (7, "Iyul"), (8, "Avgust"), (9, "Sentyabr"), (10, "Oktyabr"), (11, "Noyabr"), (12, "Dekabr")
    ]
    years_list = [today.year - 1, today.year, today.year + 1]

    context = {
        'employee': employee,
        'weekly_attendances': weekly_attendances,
        'monthly_attendances': monthly_attendances,
        'w_stats': w_stats,
        'm_stats': m_stats,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'current_month': month,
        'current_year': year,
        'months_list': months_list,
        'years_list': years_list,
    }
    return render(request, 'attendance/user_monitoring.html', context)