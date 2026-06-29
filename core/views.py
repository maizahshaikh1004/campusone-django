from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from academics.models import Subject,Notice, Event, EventCoordinator, AttendanceRecord, Timetable, FacultySubject
from users.models import Profile
from django.utils import timezone
from assignments.models import Assignment, AssignmentSubmission
from datetime import datetime

def home(request):
    return render(request,'home.html')

@login_required
def student_dashboard(request):
    profile=request.user.profile
    #context={"name": request.user.username}
    if profile.role != "STUDENT":
        return render(request,"403.html", 
        {
            "message": "Students only"
        }, 
        status=403)

    student_class = profile.academic_class
    student_department = student_class.department

    recent_notices = (
    Notice.objects.filter(
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
    )
    .order_by("-created_at")[:5]
    )
    

    notice_count = (
    Notice.objects.filter(
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
    )
    .count()
    )

    

    upcoming_events = (
        Event.objects.filter(
            Q(event_type="GENERAL")
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
            event_date__gte=timezone.now(),
            is_active=True
        )
        .order_by("event_date")[:5]
    )

    upcoming_events_count = (
    Event.objects.filter(
        Q(event_type="GENERAL")
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
        event_date__gte=timezone.now(),
        is_active=True
    )
    .count()
)
    total_subjects = Subject.objects.filter(
    academic_class=student_class
).count()


    class_assignments = Assignment.objects.filter(
    faculty_subject__subject__academic_class=student_class
)

    submitted_assignments = AssignmentSubmission.objects.filter(
    student=profile
).values_list(
    "assignment_id",
    flat=True
)

    pending_assignments = class_assignments.exclude(
    id__in=submitted_assignments
).order_by("due_date")

    pending_assignments_count = pending_assignments.count()

    coordinator_events_count = (
    EventCoordinator.objects.filter(
        student=profile
    ).count()
)
    total_lectures = AttendanceRecord.objects.filter(
    student=profile
).count()

    present_lectures = AttendanceRecord.objects.filter(
    student=profile,
    is_present=True
).count()

    if total_lectures > 0:
        attendance_percentage = round(
            (present_lectures / total_lectures) * 100,
            1
        )
    else:
        attendance_percentage = 0

    coordinator_events_count = EventCoordinator.objects.filter(
    student=profile
).count()

    ##timetable
    today=datetime.now().strftime("%A").upper()
    today_lectures=Timetable.objects.filter(
        faculty_subject__subject__academic_class=student_class,day=today
    )
    today_lectures_count=today_lectures.count()


    context = {
    "name": profile.full_name,
    "recent_notices": recent_notices,
    "notice_count": notice_count,
    "upcoming_events":upcoming_events,
    "upcoming_events_count":upcoming_events_count,
    "total_subjects": total_subjects,
    "pending_assignments": pending_assignments[:5],
    "pending_assignments_count": pending_assignments_count,
    "coordinator_events_count":coordinator_events_count,
    "attendance_percentage": attendance_percentage,
    "today_lectures_count":today_lectures_count,
    }


    return render(
        request,
        "student/dashboard.html",
        context
    )





@login_required
def faculty_dashboard(request):

    profile = request.user.profile

    if profile.role != "FACULTY":
        return render(
            request,
            "403.html",
            {"message": "Faculty Only."},
            status=403
        )

    total_subjects = FacultySubject.objects.filter(
        faculty=profile
    ).count()

    total_assignments = Assignment.objects.filter(
        faculty_subject__faculty=profile
    ).count()

    total_events = Event.objects.filter(
        faculty_incharge=profile,
        is_active=True
    ).count()

    total_notices = Notice.objects.filter(
        created_by=profile
    ).count()

    recent_assignments = (
        Assignment.objects.filter(
            faculty_subject__faculty=profile
        )
        .select_related(
            "faculty_subject__subject"
        )
        .order_by("-created_at")[:5]
    )

    upcoming_events = (
        Event.objects.filter(
            faculty_incharge=profile,
            is_active=True
        )
        .order_by("event_date")[:5]
    )

    recent_notices = (
    Notice.objects.filter(
        created_by=profile
    )
    .order_by("-created_at")[:5]
)

    pending_submissions = 0

    assignments = Assignment.objects.filter(
        faculty_subject__faculty=profile
    ).select_related(
        "faculty_subject__subject__academic_class"
    )

    for assignment in assignments:

        total_students = assignment.faculty_subject.subject.academic_class.profile_set.filter(
            role="STUDENT"
        ).count()

        submitted = AssignmentSubmission.objects.filter(
            assignment=assignment
        ).count()

        pending_submissions += max(
            total_students - submitted,
            0
        )

    context = {

        "name": profile.full_name,

        "total_subjects": total_subjects,
        "total_assignments": total_assignments,
        "total_events": total_events,
        "total_notices": total_notices,

        "pending_submissions": pending_submissions,

        "recent_assignments": recent_assignments,
        "upcoming_events": upcoming_events,
    }

    return render(
        request,
        "faculty/dashboard.html",
        context
    )