from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from users.models import Profile
from django.utils import timezone
from datetime import datetime
from academics.models import Notice, Event, EventCoordinator
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