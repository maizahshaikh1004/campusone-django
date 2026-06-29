from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from users.models import Profile
from django.utils import timezone
from datetime import datetime
from academics.models import Notice, Event, EventCoordinator, Subject, AttendanceRecord, FacultySubject

# Create your views here.

@login_required
def student_notices(request):

    profile = request.user.profile

    student_class = profile.academic_class
    student_department = student_class.department

    notices = Notice.objects.filter(
        Q(notice_type="GENERAL")
        |
        Q(
            notice_type="DEPARTMENT",
            department=student_department
        )
        |
        Q(
            notice_type="CLASS",
            academic_class=student_class
        )
    ).order_by("-created_at")

    return render(
        request,
        "student/student_notices.html",
        {
            "notices": notices
        }
    )

@login_required
def student_events(request):

    profile = request.user.profile

    if profile.role != "STUDENT":
        return render(
            request,
            "403.html",
            {
                "message": "Students Only."
            },
            status=403
        )

    student_class = profile.academic_class
    student_department = student_class.department

    events = (
        Event.objects.filter(
            Q(
                event_type="GENERAL"
            )
            |
            Q(
                event_type="DEPARTMENT",
                department=student_department
            )
            |
            Q(
                event_type="CLASS",
                academic_class=student_class
            ),
            is_active=True
        )
        .order_by(
            "event_date",
            "start_time"
        )
    )

    return render(
        request,
        "student/student_events.html",
        {
            "events": events
        }
    )

from django.shortcuts import get_object_or_404


@login_required
def event_detail(request, event_id):

    profile = request.user.profile

    if profile.role not in [
        "STUDENT",
        "FACULTY",
        "ADMIN"
    ]:
        return render(
            request,
            "403.html",
            {
                "message": "Not Allowed."
            },
            status=403
        )

    event = get_object_or_404(
        Event,
        pk=event_id,
        is_active=True
    )

    return render(
        request,
        "student/event_detail.html",
        {
            "event": event
        }
    )


@login_required
def student_attendance(request):

    profile = request.user.profile

    if profile.role != "STUDENT":
        return render(
            request,
            "403.html",
            {"message": "Students Only."},
            status=403
        )

    student_class = profile.academic_class

    subjects = Subject.objects.filter(
        academic_class=student_class
    )

    attendance_data = []

    for subject in subjects:

        records = AttendanceRecord.objects.filter(
            student=profile,
            attendance_session__timetable__faculty_subject__subject=subject
        )

        total = records.count()

        present = records.filter(
            is_present=True
        ).count()

        percentage = (
            round((present / total) * 100, 1)
            if total > 0 else 0
        )

        attendance_data.append({
            "subject_id": subject.id,
            "subject_name": subject.name,
            "total": total,
            "present": present,
            "percentage": percentage,
        })

    return render(
        request,
        "student/student_attendance.html",
        {
            "attendance_data": attendance_data
        }
    )

@login_required
def student_attendance_detail(
    request,
    subject_id
):

    profile = request.user.profile

    subject = Subject.objects.get(
        pk=subject_id
    )

    records = AttendanceRecord.objects.filter(
        student=profile,
        attendance_session__timetable__faculty_subject__subject=subject
    ).select_related(
        "attendance_session",
        "attendance_session__timetable"
    ).order_by(
        "-attendance_session__lecture_date"
    )

    total = records.count()

    present = records.filter(
        is_present=True
    ).count()

    absent = total - present

    percentage = (
        round((present / total) * 100, 1)
        if total > 0 else 0
    )

    attendance_records = []

    for record in records:

        timetable = (
            record
            .attendance_session
            .timetable
        )

        attendance_records.append({
            "date":
                record.attendance_session.lecture_date,

            "present":
                record.is_present,

            "day":
                timetable.day,

            "start":
                timetable.start_time,

            "end":
                timetable.end_time,
        })

    context = {
        "subject_name": subject.name,
        "total": total,
        "present": present,
        "absent": absent,
        "percentage": percentage,
        "attendance_records": attendance_records,
    }

    return render(
        request,
        "student/student_attendance_detail.html",
        context
    )

@login_required
def student_subjects(request):

    profile = request.user.profile

    if profile.role != "STUDENT":
        return render(
            request,
            "403.html",
            {"message": "Students Only."},
            status=403
        )

    subjects = Subject.objects.filter(
        academic_class=profile.academic_class
    )

    return render(
        request,
        "student/student_subjects.html",
        {
            "subjects": subjects
        }
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from academics.models import Timetable


@login_required
def student_timetable(request):

    profile = request.user.profile

    if profile.role != "STUDENT":
        return render(
            request,
            "403.html",
            {
                "message": "Students Only."
            },
            status=403
        )

    timetable_entries = (
        Timetable.objects.filter(
            faculty_subject__subject__academic_class=
            profile.academic_class
        )
        .select_related(
            "faculty_subject",
            "faculty_subject__subject",
            "faculty_subject__faculty"
        )
        .order_by(
            "day",
            "start_time"
        )
    )

    return render(
        request,
        "student/student_timetable.html",
        {
            "timetable_entries": timetable_entries
        }
    )


@login_required
def student_coordinator_events(request):

    profile = request.user.profile

    if profile.role != "STUDENT":
        return render(
            request,
            "403.html",
            {"message": "Students Only."},
            status=403
        )

    today = timezone.localdate()

    events = (
        EventCoordinator.objects.filter(
            student=profile,
            event__is_active=True,
            event__event_date__gte=today
        )
        .select_related("event")
        .order_by("event__event_date")
    )

    return render(
        request,
        "student/student_coordinator_events.html",
        {
            "events": events
        }
    )

@login_required
def student_past_coordinator_events(request):

    profile = request.user.profile

    if profile.role != "STUDENT":
        return render(
            request,
            "403.html",
            {"message": "Students Only."},
            status=403
        )

    today = timezone.localdate()

    past_events = (
        EventCoordinator.objects.filter(
            student=profile,
            event__is_active=True,
            event__event_date__lt=today
        )
        .select_related("event")
        .order_by("-event__event_date")
    )

    return render(
        request,
        "student/student_past_coordinator_events.html",
        {
            "past_events": past_events
        }
    )


@login_required
def faculty_subjects(request):

    profile = request.user.profile

    if profile.role != "FACULTY":
        return render(
            request,
            "403.html",
            {
                "message": "Faculty Only."
            },
            status=403
        )

    subjects = (
        FacultySubject.objects.filter(
            faculty=profile
        )
        .select_related(
            "subject",
            "subject__academic_class",
            "subject__academic_class__department"
        )
        .order_by(
            "subject__name"
        )
    )

    context = {
        "subjects": subjects
    }

    return render(
        request,
        "faculty/faculty_subjects.html",
        context
    )


@login_required
def faculty_notices(request):
    return HttpResponse("Faculty Notices - Coming Soon")


@login_required
def faculty_events(request):
    return HttpResponse("Faculty Events - Coming Soon")