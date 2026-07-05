from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from users.models import Profile
from django.utils import timezone
from datetime import datetime, date
from django.core.exceptions import ValidationError
from academics.models import (
    Notice, Event, EventCoordinator, Subject, AttendanceRecord, FacultySubject,
    Department, AcademicClass, Semester, Timetable, AttendanceSession, AttendanceCorrectionRequest
)

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
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    faculty_dept = profile.department
    faculty_class = profile.academic_class

    notices_qs = Notice.objects.filter(
        Q(created_by=profile) |
        Q(notice_type='GENERAL') |
        Q(notice_type='DEPARTMENT', department=faculty_dept) |
        Q(notice_type='CLASS', academic_class=faculty_class)
    ).select_related('department', 'academic_class__semester', 'created_by').distinct().order_by('-created_at')

    return render(request, 'faculty/faculty_notices.html', {'notices': notices_qs})


@login_required
def create_notice(request):
    profile = request.user.profile
    if profile.role not in ['ADMIN', 'FACULTY']:
        return render(request, '403.html', {'message': 'Admins or Faculty Only.'}, status=403)

    if profile.role == 'ADMIN':
        departments_qs = Department.objects.all()
    else:
        departments_qs = Department.objects.filter(id=profile.department_id)
    departments = [(d.id, d.name) for d in departments_qs]

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        scope = request.POST.get('scope')
        attachment = request.FILES.get('attachment')

        department_id = request.POST.get('department_id')
        semester_id = request.POST.get('semester_id')

        notice = Notice(
            title=title,
            content=content,
            created_by=profile
        )

        if scope == 'GLOBAL':
            notice.notice_type = 'GENERAL'
        elif scope == 'DEPARTMENT':
            if semester_id:
                academic_class = AcademicClass.objects.filter(department_id=department_id, semester_id=semester_id).first()
                if academic_class:
                    notice.notice_type = 'CLASS'
                    notice.academic_class = academic_class
                else:
                    messages.error(request, "Selected Class/Semester not found.")
                    return render(request, 'faculty/create_notice.html', {
                        'departments': departments,
                        'form_data': request.POST
                    })
            else:
                notice.notice_type = 'DEPARTMENT'
                notice.department_id = department_id

        if attachment:
            notice.attachment = attachment

        try:
            notice.full_clean()
            notice.save()
            messages.success(request, "Notice posted successfully ✅")
            return redirect('admin_notices' if profile.role == 'ADMIN' else 'faculty_notices')
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return render(request, 'faculty/create_notice.html', {
                'departments': departments,
                'form_data': request.POST
            })
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'faculty/create_notice.html', {
                'departments': departments,
                'form_data': request.POST
            })

    return render(request, 'faculty/create_notice.html', {
        'departments': departments
    })


@login_required
def edit_notice(request, notice_id):
    profile = request.user.profile
    if profile.role not in ['ADMIN', 'FACULTY']:
        return render(request, '403.html', {'message': 'Not Allowed.'}, status=403)

    notice = get_object_or_404(Notice, id=notice_id)

    if profile.role == 'FACULTY' and notice.created_by != profile:
        return render(request, '403.html', {'message': 'You can only edit your own notices.'}, status=403)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        remove_attachment = request.POST.get('remove_attachment')
        new_attachment = request.FILES.get('attachment')

        notice.title = title
        notice.content = content

        if remove_attachment:
            notice.attachment = None

        if new_attachment:
            notice.attachment = new_attachment

        try:
            notice.full_clean()
            notice.save()
            messages.success(request, "Notice updated successfully ✅")
            return redirect('admin_notices' if profile.role == 'ADMIN' else 'faculty_notices')
        except ValidationError as e:
            messages.error(request, e.messages[0])
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'faculty/edit_notice.html', {
        'notice': notice
    })


@login_required
def delete_notice(request, notice_id):
    profile = request.user.profile
    if profile.role not in ['ADMIN', 'FACULTY']:
        return render(request, '403.html', {'message': 'Not Allowed.'}, status=403)

    notice = get_object_or_404(Notice, id=notice_id)

    if profile.role == 'FACULTY' and notice.created_by != profile:
        return render(request, '403.html', {'message': 'You can only delete your own notices.'}, status=403)

    notice.delete()
    messages.success(request, "Notice deleted successfully.")
    return redirect('admin_notices' if profile.role == 'ADMIN' else 'faculty_notices')


@login_required
def notice_detail(request, notice_id):
    profile = request.user.profile
    if profile.role not in ['ADMIN', 'FACULTY', 'STUDENT']:
        return render(request, '403.html', {'message': 'Not Allowed.'}, status=403)

    notice = get_object_or_404(Notice.objects.select_related('created_by', 'department', 'academic_class__semester'), id=notice_id)
    
    return render(request, 'faculty/notice_detail.html', {
        'notice': notice
    })


@login_required
def faculty_events(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    readonly = request.GET.get("mode") == "view_all"

    events_qs = Event.objects.filter(
        Q(created_by=profile) |
        Q(faculty_incharge=profile) |
        Q(event_type='GENERAL') |
        Q(event_type='DEPARTMENT', department=profile.department) |
        Q(event_type='CLASS', academic_class=profile.academic_class)
    ).select_related('department', 'academic_class__semester', 'created_by', 'faculty_incharge').distinct().order_by('event_date', 'start_time')

    events = list(events_qs)
    for e in events:
        e.can_edit = (e.created_by == profile or e.faculty_incharge == profile)
        e.can_delete = (e.created_by == profile or e.faculty_incharge == profile)
        e.can_assign = (e.created_by == profile or e.faculty_incharge == profile)

    return render(request, 'faculty/faculty_events.html', {
        'events': events,
        'readonly': False
    })


@login_required
def faculty_events_only(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    events_qs = Event.objects.filter(
        Q(created_by=profile) |
        Q(faculty_incharge=profile) |
        Q(event_type='GENERAL') |
        Q(event_type='DEPARTMENT', department=profile.department) |
        Q(event_type='CLASS', academic_class=profile.academic_class)
    ).select_related('department', 'academic_class__semester', 'created_by', 'faculty_incharge').distinct().order_by('event_date', 'start_time')

    events = list(events_qs)
    for e in events:
        e.can_edit = (e.created_by == profile or e.faculty_incharge == profile)
        e.can_delete = (e.created_by == profile or e.faculty_incharge == profile)
        e.can_assign = (e.created_by == profile or e.faculty_incharge == profile)

    return render(request, 'faculty/faculty_events.html', {
        'events': events,
        'readonly': False
    })


@login_required
def create_event(request):
    profile = request.user.profile
    if profile.role not in ['ADMIN', 'FACULTY']:
        return render(request, '403.html', {'message': 'Only Admin or Faculty can create events.'}, status=403)

    departments_qs = Department.objects.all()
    departments = [(d.id, d.name) for d in departments_qs]

    semesters_qs = Semester.objects.all()
    semesters = [(s.id, s.semester_number) for s in semesters_qs]

    faculties = []
    if profile.role == 'ADMIN':
        faculties_qs = Profile.objects.filter(role='FACULTY')
        faculties = [(f.id, f.full_name) for f in faculties_qs]

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        event_date = request.POST.get('event_date', '').strip()
        start_time = request.POST.get('start_time', '').strip()
        end_time = request.POST.get('end_time', '').strip()
        venue = request.POST.get('venue', '').strip()
        google_form_link = request.POST.get('google_form_link', '').strip()

        department_id = request.POST.get('department_id') or None
        semester_id = request.POST.get('semester_id') or None

        if profile.role == 'FACULTY':
            faculty_incharge = profile
        else:
            faculty_incharge_id = request.POST.get('faculty_incharge_id')
            if faculty_incharge_id:
                faculty_incharge = get_object_or_404(Profile, id=faculty_incharge_id)
            else:
                faculty_incharge = profile

        poster = request.FILES.get('poster')

        event = Event(
            title=title,
            description=description,
            event_date=event_date if event_date else None,
            start_time=start_time if start_time else None,
            end_time=end_time if end_time else None,
            venue=venue,
            google_form_link=google_form_link,
            created_by=profile,
            faculty_incharge=faculty_incharge
        )

        if department_id:
            if semester_id:
                academic_class = AcademicClass.objects.filter(department_id=department_id, semester_id=semester_id).first()
                if academic_class:
                    event.event_type = 'CLASS'
                    event.academic_class = academic_class
                else:
                    messages.error(request, "Selected Class/Semester not found.")
                    return render(request, 'faculty/create_event.html', {
                        'role': profile.role,
                        'departments': departments,
                        'semesters': semesters,
                        'faculties': faculties,
                        'form_data': request.POST
                    })
            else:
                event.event_type = 'DEPARTMENT'
                event.department_id = department_id
        else:
            event.event_type = 'GENERAL'

        if poster:
            event.poster = poster

        try:
            event.full_clean()
            event.save()
            messages.success(request, "Event created successfully ✅")
            return redirect('admin_events' if profile.role == 'ADMIN' else 'faculty_events')
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return render(request, 'faculty/create_event.html', {
                'role': profile.role,
                'departments': departments,
                'semesters': semesters,
                'faculties': faculties,
                'form_data': request.POST
            })
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'faculty/create_event.html', {
                'role': profile.role,
                'departments': departments,
                'semesters': semesters,
                'faculties': faculties,
                'form_data': request.POST
            })

    return render(request, 'faculty/create_event.html', {
        'role': profile.role,
        'departments': departments,
        'semesters': semesters,
        'faculties': faculties
    })


@login_required
def edit_event(request, event_id):
    profile = request.user.profile
    if profile.role not in ['ADMIN', 'FACULTY']:
        return render(request, '403.html', {'message': 'Not Allowed.'}, status=403)

    event = get_object_or_404(Event, id=event_id)

    if profile.role == 'FACULTY' and event.created_by != profile and event.faculty_incharge != profile:
        return render(request, '403.html', {'message': 'You are not allowed to edit this event.'}, status=403)

    if request.method == 'POST':
        event.title = request.POST.get('title', '').strip()
        event.description = request.POST.get('description', '').strip()
        event.event_date = request.POST.get('event_date')
        event.start_time = request.POST.get('start_time')
        event.end_time = request.POST.get('end_time')
        event.venue = request.POST.get('venue', '').strip()
        event.google_form_link = request.POST.get('google_form_link', '').strip()

        poster = request.FILES.get('poster')
        if poster:
            event.poster = poster

        try:
            event.full_clean()
            event.save()
            messages.success(request, "Event updated successfully ✅")
            return redirect('admin_events' if profile.role == 'ADMIN' else 'faculty_events')
        except ValidationError as e:
            messages.error(request, e.messages[0])
        except Exception as e:
            messages.error(request, str(e))

    return render(request, 'faculty/edit_event.html', {
        'event': event
    })


@login_required
def delete_event(request, event_id):
    profile = request.user.profile
    if profile.role not in ['ADMIN', 'FACULTY']:
        return render(request, '403.html', {'message': 'Not Allowed.'}, status=403)

    event = get_object_or_404(Event, id=event_id)

    if profile.role == 'FACULTY' and event.created_by != profile and event.faculty_incharge != profile:
        return render(request, '403.html', {'message': 'You are not allowed to delete this event.'}, status=403)

    if request.method == 'POST':
        event.is_active = False
        event.save()
        return redirect('admin_events' if profile.role == 'ADMIN' else 'faculty_events')

    return render(request, 'faculty/confirm_delete_event.html', {
        'event_id': event.id
    })


@login_required
def assign_event_coordinators(request, event_id):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    event = get_object_or_404(Event, id=event_id, is_active=True)

    if event.created_by != profile and event.faculty_incharge != profile:
        return render(request, '403.html', {'message': 'You are not allowed to manage coordinators for this event.'}, status=403)

    error = None

    if request.method == 'POST':
        remove_id = request.POST.get('remove_id')
        student_id = request.POST.get('student_id')

        if remove_id:
            EventCoordinator.objects.filter(event=event, student_id=remove_id).delete()
            return redirect('assign_event_coordinators', event_id=event.id)

        if student_id:
            if EventCoordinator.objects.filter(event=event).count() >= 2:
                error = "Maximum 2 coordinators allowed."
            else:
                student = get_object_or_404(Profile, id=student_id, role='STUDENT')
                try:
                    coord = EventCoordinator(event=event, student=student)
                    coord.full_clean()
                    coord.save()
                    return redirect(f"{request.path}?success=1")
                except ValidationError as e:
                    error = e.messages[0]

    assigned_qs = EventCoordinator.objects.filter(event=event).select_related('student')
    assigned_count = assigned_qs.count()
    remaining_slots = 2 - assigned_count

    assigned_ids = assigned_qs.values_list('student_id', flat=True)
    students_qs = Profile.objects.filter(
        role='STUDENT',
        user__is_active=True
    ).exclude(id__in=assigned_ids).order_by('full_name')

    return render(request, 'faculty/assign_event_coordinators.html', {
        'assigned': assigned_qs,
        'students': students_qs,
        'error': error,
        'assigned_count': assigned_count,
        'remaining_slots': remaining_slots,
        'event_id': event.id
    })


def get_semesters_by_department(request):
    dept_id = request.GET.get('department_id')
    if not dept_id:
        return JsonResponse([], safe=False)
    
    semesters = Semester.objects.filter(
        academicclass__department_id=dept_id
    ).distinct().order_by('semester_number')

    data = [
        {
            'id': s.id,
            'number': s.semester_number
        }
        for s in semesters
    ]
    return JsonResponse(data, safe=False)


def get_classes_by_department(request):
    dept_id = request.GET.get('department_id')
    if not dept_id:
        return JsonResponse({'classes': []})

    classes = AcademicClass.objects.filter(department_id=dept_id).order_by('name')
    data = [[c.id, c.name] for c in classes]
    return JsonResponse({'classes': data})


def get_semesters_by_class(request):
    class_id = request.GET.get('class_id')
    semesters = Semester.objects.filter(academicclass__id=class_id).distinct().order_by('semester_number')
    data = [[s.id, s.semester_number] for s in semesters]
    return JsonResponse({'semesters': data})


def get_subjects_by_semester(request):
    semester_id = request.GET.get('semester_id')
    if not semester_id:
        return JsonResponse({'subjects': []})

    # In refactored models, Subject doesn't have semester_id directly, but AcademicClass does.
    # So we get Subjects belonging to any AcademicClass of that semester:
    subjects = Subject.objects.filter(academic_class__semester_id=semester_id).order_by('name')
    data = [[s.id, s.name] for s in subjects]
    return JsonResponse({'subjects': data})

@login_required
def get_subjects_by_class(request):
    class_id = request.GET.get('class_id')
    if not class_id:
        return JsonResponse([], safe=False)
    
    profile = request.user.profile
    if profile.role == 'ADMIN':
        subjects = Subject.objects.filter(
            academic_class_id=class_id
        ).distinct().order_by('name')
    else:
        subjects = Subject.objects.filter(
            academic_class_id=class_id,
            facultysubject__faculty=profile
        ).distinct().order_by('name')
    
    data = [{'id': s.id, 'name': s.name} for s in subjects]
    return JsonResponse(data, safe=False)


@login_required
def get_timetable_slots(request):
    class_id = request.GET.get('class_id')
    subject_id = request.GET.get('subject_id')
    if not class_id or not subject_id:
        return JsonResponse([], safe=False)
    
    profile = request.user.profile
    slots = Timetable.objects.filter(
        faculty_subject__faculty=profile,
        faculty_subject__subject__academic_class_id=class_id,
        faculty_subject__subject_id=subject_id
    ).select_related('faculty_subject__subject').order_by('day', 'start_time')
    
    data = [
        {
            'id': t.id,
            'day': t.day.title(),
            'start_time': t.start_time.strftime('%H:%M'),
            'end_time': t.end_time.strftime('%H:%M')
        }
        for t in slots
    ]
    return JsonResponse(data, safe=False)


@login_required
def faculty_timetable(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    timetable_entries = Timetable.objects.filter(
        faculty_subject__faculty=profile
    ).select_related(
        'faculty_subject__subject',
        'faculty_subject__subject__academic_class'
    ).order_by('day', 'start_time')

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_map = {d.upper(): d for d in days}

    timetable = {}
    time_slots = []

    for entry in timetable_entries:
        start_str = entry.start_time.strftime('%H:%M')
        end_str = entry.end_time.strftime('%H:%M')
        slot = f"{start_str}-{end_str}"

        if slot not in timetable:
            timetable[slot] = {}
            time_slots.append(slot)

        display_day = day_map.get(entry.day, entry.day)
        timetable[slot][display_day] = f"{entry.faculty_subject.subject.name} ({entry.faculty_subject.subject.academic_class.name})"

    grid = []
    for slot in time_slots:
        row = {
            'time': slot,
            'cells': [timetable.get(slot, {}).get(day, '---') for day in days]
        }
        grid.append(row)

    return render(request, 'faculty/faculty_timetable.html', {
        'days': days,
        'grid': grid
    })


@login_required
def mark_attendance(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    classes_qs = AcademicClass.objects.filter(
        subject__facultysubject__faculty=profile
    ).distinct()

    students = []
    selected_class_id = None
    selected_subject_id = None
    selected_date = None
    selected_timetable_id = None

    if request.method == 'POST':
        selected_class_id = request.POST.get('class_id')
        selected_subject_id = request.POST.get('subject_id')
        selected_date = request.POST.get('lecture_date')
        selected_timetable_id = request.POST.get('timetable_id')

        # Date validation
        is_future_date = False
        if selected_date:
            try:
                lecture_date_parsed = datetime.strptime(selected_date, '%Y-%m-%d').date()
                if lecture_date_parsed > date.today():
                    is_future_date = True
                    messages.error(request, "Cannot mark attendance for future dates.")
            except ValueError:
                messages.error(request, "Invalid date format.")
                is_future_date = True

        if not is_future_date:
            if 'load_students' in request.POST:
                students = Profile.objects.filter(
                    role='STUDENT',
                    academic_class_id=selected_class_id,
                    user__is_active=True
                ).order_by('full_name')
            else:
                present_students = request.POST.getlist('present_students')
                all_students_qs = Profile.objects.filter(
                    role='STUDENT',
                    academic_class_id=selected_class_id,
                    user__is_active=True
                )

                try:
                    from django.db import transaction
                    with transaction.atomic():
                        lecture_date_parsed = datetime.strptime(selected_date, '%Y-%m-%d').date()
                        session, created = AttendanceSession.objects.get_or_create(
                            timetable_id=selected_timetable_id,
                            lecture_date=lecture_date_parsed
                        )

                        for student in all_students_qs:
                            is_present = str(student.id) in present_students
                            AttendanceRecord.objects.update_or_create(
                                attendance_session=session,
                                student=student,
                                defaults={'is_present': is_present}
                            )

                    messages.success(
                        request,
                        f"Attendance marked successfully. "
                        f"{len(present_students)} Present, "
                        f"{all_students_qs.count() - len(present_students)} Absent."
                    )
                    return redirect('faculty_dashboard')
                except Exception as e:
                    messages.error(request, f"Error occurred: {str(e)}")

    if selected_class_id:
        subjects_qs = Subject.objects.filter(
            academic_class_id=selected_class_id,
            facultysubject__faculty=profile
        ).distinct().order_by('name')
    else:
        subjects_qs = Subject.objects.none()

    if selected_class_id and selected_subject_id:
        timetable_slots_qs = Timetable.objects.filter(
            faculty_subject__faculty=profile,
            faculty_subject__subject__academic_class_id=selected_class_id,
            faculty_subject__subject_id=selected_subject_id
        ).select_related('faculty_subject__subject').order_by('day', 'start_time')
    else:
        timetable_slots_qs = Timetable.objects.none()

    return render(request, 'faculty/faculty_mark_attendance.html', {
        'classes': classes_qs,
        'subjects': subjects_qs,
        'timetable_slots': timetable_slots_qs,
        'students': students,
        'selected_class_id': selected_class_id,
        'selected_subject_id': selected_subject_id,
        'selected_date': selected_date,
        'selected_timetable_id': selected_timetable_id,
    })


@login_required
def faculty_view_attendance(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    records_qs = AttendanceRecord.objects.filter(
        attendance_session__timetable__faculty_subject__faculty=profile
    ).select_related(
        'student',
        'attendance_session__timetable__faculty_subject__subject',
        'attendance_session__timetable'
    ).order_by('-attendance_session__lecture_date', 'attendance_session__timetable__start_time')

    return render(request, 'faculty/faculty_view_attendance.html', {
        'records': records_qs
    })


@login_required
def faculty_attendance_report(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    faculty_subjects = FacultySubject.objects.filter(
        faculty=profile
    ).select_related('subject', 'subject__academic_class', 'subject__academic_class__department')

    report = []
    for fs in faculty_subjects:
        students = Profile.objects.filter(
            role='STUDENT',
            academic_class=fs.subject.academic_class,
            user__is_active=True
        ).order_by('full_name')

        for student in students:
            records = AttendanceRecord.objects.filter(
                student=student,
                attendance_session__timetable__faculty_subject=fs
            )
            total = records.count()
            present = records.filter(is_present=True).count()
            percentage = round((present / total) * 100, 1) if total > 0 else 0.0

            report.append({
                'student': student,
                'class_name': fs.subject.academic_class.name,
                'subject_name': fs.subject.name,
                'percentage': percentage
            })

    return render(request, 'faculty/faculty_attendance_report.html', {
        'report': report
    })


@login_required
def request_attendance_correction(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    records_qs = AttendanceRecord.objects.filter(
        attendance_session__timetable__faculty_subject__faculty=profile
    ).select_related(
        'student',
        'attendance_session__timetable__faculty_subject__subject'
    ).order_by('-attendance_session__lecture_date')

    message = None
    error = None

    if request.method == 'POST':
        attendance_id = request.POST.get('attendance_id')
        new_status = request.POST.get('new_status') == '1'
        reason = request.POST.get('reason')

        if not attendance_id or not reason:
            error = "Please select a record and provide reason."
        else:
            attendance_record = get_object_or_404(AttendanceRecord, id=attendance_id)
            try:
                correction_req = AttendanceCorrectionRequest(
                    attendance_record=attendance_record,
                    faculty=profile,
                    requested_is_present=new_status,
                    reason=reason
                )
                correction_req.full_clean()
                correction_req.save()
                message = "Correction request submitted successfully."
            except ValidationError as e:
                error = e.messages[0]
            except Exception as e:
                error = str(e)

    return render(request, 'faculty/faculty_request_correction.html', {
        'attendance_records': records_qs,
        'message': message,
        'error': error
    })