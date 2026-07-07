from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from academics.models import Subject, Notice, Event, EventCoordinator, AttendanceRecord, Timetable, FacultySubject, AttendanceCorrectionRequest, Department, Semester, AcademicClass
from users.models import Profile, RegistrationRequest
from django.utils import timezone
from assignments.models import Assignment, AssignmentSubmission
from datetime import datetime
from django.core.mail import send_mail
import pandas as pd


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
            Q(created_by=profile) |
            Q(faculty_incharge=profile) |
            Q(event_type='GENERAL') |
            Q(event_type='DEPARTMENT', department=profile.department) |
            Q(event_type='CLASS', academic_class=profile.academic_class),
            is_active=True
        )
        .order_by("event_date")[:5]
    )

    recent_notices = (
        Notice.objects.filter(
            Q(created_by=profile) |
            Q(notice_type='GENERAL') |
            Q(notice_type='DEPARTMENT', department=profile.department) |
            Q(notice_type='CLASS', academic_class=profile.academic_class)
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
        "recent_notices": recent_notices,
    }

    return render(
        request,
        "faculty/dashboard.html",
        context
    )


@login_required
def admin_dashboard(request):
    profile = request.user.profile
    if profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    total_students = Profile.objects.filter(role='STUDENT').count()
    total_faculty = Profile.objects.filter(role='FACULTY').count()
    pending_registrations = RegistrationRequest.objects.filter(status='PENDING').count()
    pending_corrections = AttendanceCorrectionRequest.objects.filter(status='PENDING').count()

    recent_notices = Notice.objects.all().order_by('-created_at')[:5]
    upcoming_events = Event.objects.filter(event_date__gte=timezone.now(), is_active=True).order_by('event_date')[:5]
    recent_registrations = RegistrationRequest.objects.filter(status='PENDING').order_by('-requested_at')[:5]

    context = {
        'profile': profile,
        'total_students': total_students,
        'total_faculty': total_faculty,
        'pending_registrations': pending_registrations,
        'pending_corrections': pending_corrections,
        'recent_notices': recent_notices,
        'upcoming_events': upcoming_events,
        'recent_registrations': recent_registrations,
    }

    return render(request, 'admin/admin_dashboard.html', context)


@login_required
def admin_students_list(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    search = request.GET.get('search', '').strip()
    dept_id = request.GET.get('department', '')
    class_id = request.GET.get('class', '')
    sem_id = request.GET.get('semester', '')

    students = Profile.objects.filter(role='STUDENT').select_related(
        'user', 'department', 'academic_class__semester'
    )

    if search:
        students = students.filter(
            Q(full_name__icontains=search) | 
            Q(user__email__icontains=search) | 
            Q(user__username__icontains=search)
        )

    if dept_id:
        students = students.filter(department_id=dept_id)

    if class_id:
        students = students.filter(academic_class_id=class_id)

    if sem_id:
        students = students.filter(academic_class__semester_id=sem_id)

    students = students.order_by('full_name')

    departments = Department.objects.all().order_by('name')
    classes = AcademicClass.objects.all().order_by('name')
    semesters = Semester.objects.all().order_by('semester_number')

    return render(request, 'admin/admin_all_students.html', {
        'students': students,
        'departments': departments,
        'classes': classes,
        'semesters': semesters,
        'selected_dept': dept_id,
        'selected_class': class_id,
        'selected_sem': sem_id,
        'search_query': search,
    })


@login_required
def admin_all_faculty(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    search = request.GET.get('search', '').strip()
    dept_id = request.GET.get('department', '')
    status = request.GET.get('status', '')

    faculty = Profile.objects.filter(role='FACULTY').select_related('user', 'department')

    if search:
        faculty = faculty.filter(
            Q(full_name__icontains=search) | 
            Q(user__email__icontains=search) | 
            Q(user__username__icontains=search)
        )

    if dept_id:
        faculty = faculty.filter(department_id=dept_id)

    if status == 'active':
        faculty = faculty.filter(user__is_active=True)
    elif status == 'inactive':
        faculty = faculty.filter(user__is_active=False)

    faculty = faculty.order_by('full_name')

    departments = Department.objects.all().order_by('name')

    return render(request, 'admin/admin_all_faculty.html', {
        'faculty': faculty,
        'departments': departments,
        'selected_dept': dept_id,
        'selected_status': status,
        'search_query': search,
    })


@login_required
def toggle_user_status_view(request, profile_id):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)
        
    profile = get_object_or_404(Profile, pk=profile_id)
    user = profile.user
    
    user.is_active = not user.is_active
    user.save()
    
    status_str = "activated" if user.is_active else "deactivated"
    messages.success(request, f"User {profile.full_name} has been {status_str}.")
    
    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    if profile.role == 'STUDENT':
        return redirect('admin_students_list')
    return redirect('admin_all_faculty')


@login_required
def admin_events(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    search = request.GET.get('search', '').strip()
    events = Event.objects.filter(is_active=True).select_related('faculty_incharge', 'department', 'academic_class').order_by('-event_date')

    if search:
        events = events.filter(title__icontains=search)

    return render(request, 'admin/admin_events.html', {
        'events': events,
        'search_query': search
    })


@login_required
def admin_notices(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    search = request.GET.get('search', '').strip()
    notices = Notice.objects.all().select_related('created_by', 'department', 'academic_class').order_by('-created_at')

    if search:
        notices = notices.filter(title__icontains=search)

    return render(request, 'admin/admin_notices.html', {
        'notices': notices,
        'search_query': search
    })


@login_required
def bulk_user_upload(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return render(request, 'admin/bulk_user_upload.html', {
                'error': 'Please upload an Excel or CSV file'
            })

        filename = uploaded_file.name.lower()
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                return render(request, 'admin/bulk_user_upload.html', {
                    'error': 'Unsupported file format. Please upload a CSV or Excel file.'
                })
        except Exception as e:
            return render(request, 'admin/bulk_user_upload.html', {
                'error': f'Failed to parse file: {str(e)}'
            })

        total_rows = 0
        inserted = 0
        duplicates = 0
        invalid = 0

        all_depts = {str(d.id): d for d in Department.objects.all()}
        all_classes = {str(c.id): c for c in AcademicClass.objects.all()}

        for _, row in df.iterrows():
            total_rows += 1

            name = str(row.get('name', '')).strip()
            email = str(row.get('email', '')).strip()
            role = str(row.get('role', '')).strip().upper()

            dept_id = str(row.get('department_id', '')).split('.')[0].strip() if not pd.isna(row.get('department_id')) else ''
            class_id = str(row.get('class_id', '')).split('.')[0].strip() if not pd.isna(row.get('class_id')) else ''

            if not name or not email or role not in ['STUDENT', 'FACULTY']:
                invalid += 1
                continue

            if not dept_id or dept_id not in all_depts:
                invalid += 1
                continue

            if role == 'STUDENT' and (not class_id or class_id not in all_classes):
                invalid += 1
                continue

            if User.objects.filter(email=email).exists():
                duplicates += 1
                continue

            try:
                base_username = name.lower().replace(" ", "")
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User.objects.create(
                    username=username,
                    email=email,
                    is_active=False
                )
                profile = user.profile
                profile.full_name = name
                profile.role = role
                profile.department = all_depts[dept_id]
                if role == 'STUDENT':
                    profile.academic_class = all_classes[class_id]
                profile.save()

                subject = "CampusOne Account Activation & Password Setup"
                domain = request.get_host()
                protocol = "https" if request.is_secure() else "http"
                activation_link = f"{protocol}://{domain}/set-password/{user.id}/"
                message = (
                    f"Dear {name},\n\n"
                    f"An account has been created for you by the Administrator with the role of {role.title()}.\n"
                    f"Please click the following link to set your password and activate your account:\n"
                    f"{activation_link}\n\n"
                    f"Best regards,\n"
                    f"CampusOne Administration"
                )
                send_mail(
                    subject,
                    message,
                    'noreply@campusone.com',
                    [email],
                    fail_silently=True
                )

                inserted += 1
            except Exception:
                invalid += 1

        return render(request, 'admin/bulk_upload_result.html', {
            'total': total_rows,
            'inserted': inserted,
            'duplicates': duplicates,
            'invalid': invalid
        })

    return render(request, 'admin/bulk_user_upload.html')


@login_required
def admin_timetable(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    class_id = request.GET.get('class', '')
    dept_id = request.GET.get('department', '')

    timetable_slots = Timetable.objects.all().select_related(
        'faculty_subject__faculty',
        'faculty_subject__subject__academic_class__semester',
        'faculty_subject__subject__academic_class__department'
    )

    if class_id:
        timetable_slots = timetable_slots.filter(faculty_subject__subject__academic_class_id=class_id)
    elif dept_id:
        timetable_slots = timetable_slots.filter(faculty_subject__subject__academic_class__department_id=dept_id)

    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    day_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    slots_qs = timetable_slots.values('start_time', 'end_time').distinct().order_by('start_time')
    
    grid = []
    for slot in slots_qs:
        start = slot['start_time']
        end = slot['end_time']
        slot_label = f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
        
        row_cells = []
        for day in days:
            day_slots = timetable_slots.filter(
                start_time=start,
                end_time=end,
                day=day
            )
            row_cells.append(list(day_slots))
            
        grid.append({
            'time': slot_label,
            'cells': row_cells
        })

    classes = AcademicClass.objects.all().order_by('name')
    departments = Department.objects.all().order_by('name')

    return render(request, 'admin/admin_timetable.html', {
        'days': day_labels,
        'grid': grid,
        'classes': classes,
        'departments': departments,
        'selected_class': class_id,
        'selected_dept': dept_id
    })


@login_required
def admin_attendance_report(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    dept_id = request.GET.get('department', '')
    class_id = request.GET.get('class', '')
    subject_id = request.GET.get('subject', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '').strip()

    students = Profile.objects.filter(role='STUDENT').select_related('user', 'department', 'academic_class__semester')

    if dept_id:
        students = students.filter(department_id=dept_id)
    if class_id:
        students = students.filter(academic_class_id=class_id)
    if search:
        students = students.filter(full_name__icontains=search)

    subjects = Subject.objects.all().select_related('academic_class')
    if dept_id:
        subjects = subjects.filter(academic_class__department_id=dept_id)
    if class_id:
        subjects = subjects.filter(academic_class_id=class_id)
    if subject_id:
        subjects = subjects.filter(id=subject_id)

    report = []
    for s in students:
        student_subjects = subjects.filter(academic_class=s.academic_class)
        for subj in student_subjects:
            records = AttendanceRecord.objects.filter(
                student=s,
                attendance_session__timetable__faculty_subject__subject=subj
            )
            total = records.count()
            present = records.filter(is_present=True).count()
            percentage = round((present / total) * 100, 1) if total > 0 else 0.0

            if status == 'short' and percentage >= 75:
                continue
            if status == 'good' and percentage < 75:
                continue

            report.append({
                'student': s,
                'subject': subj,
                'class': s.academic_class,
                'percentage': percentage,
                'total': total,
                'present': present,
            })

    departments = Department.objects.all().order_by('name')
    classes = AcademicClass.objects.all().order_by('name')
    subjects_list = Subject.objects.all().order_by('name')

    return render(request, 'admin/admin_attendance_report.html', {
        'report': report,
        'departments': departments,
        'classes': classes,
        'subjects': subjects_list,
        'selected_dept': dept_id,
        'selected_class': class_id,
        'selected_subject': subject_id,
        'selected_status': status,
        'search_query': search,
    })


@login_required
def attendance_corrections_admin(request):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)
    
    requests = AttendanceCorrectionRequest.objects.filter(
        status='PENDING'
    ).select_related(
        'attendance_record__student',
        'attendance_record__attendance_session__timetable__faculty_subject__subject',
        'faculty'
    ).order_by('-requested_at')
    
    return render(request, 'admin/admin_attendance_corrections.html', {
        'requests': requests
    })


@login_required
def approve_attendance_correction_view(request, request_id):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    req = get_object_or_404(AttendanceCorrectionRequest, pk=request_id, status='PENDING')
    
    # Update attendance record status
    record = req.attendance_record
    record.is_present = req.requested_is_present
    record.save()
    
    # Update correction request status
    req.status = 'APPROVED'
    req.reviewed_at = timezone.now()
    req.save()
    
    status_text = 'Present' if req.requested_is_present else 'Absent'
    messages.success(
        request, 
        f"Approved: {req.attendance_record.student.full_name}'s status changed to {status_text}."
    )
    return redirect('attendance_corrections_admin')


@login_required
def reject_attendance_correction_view(request, request_id):
    if request.user.profile.role != 'ADMIN':
        return render(request, '403.html', {'message': 'Admins Only.'}, status=403)

    req = get_object_or_404(AttendanceCorrectionRequest, pk=request_id, status='PENDING')
    
    if request.method == 'POST':
        remark = request.POST.get('remark', '').strip()
        if not remark:
            return render(request, 'admin/admin_reject_attendance.html', {
                'error': 'Please provide a reason for rejection.',
                'request_data': req
            })
            
        req.status = 'REJECTED'
        req.admin_remark = remark
        req.reviewed_at = timezone.now()
        req.save()
        
        messages.success(
            request, 
            f"Rejected: Correction request for {req.attendance_record.student.full_name} has been rejected."
        )
        return redirect('attendance_corrections_admin')

    return render(request, 'admin/admin_reject_attendance.html', {
        'request_data': req
    })


@login_required
def admin_redirect(request):
    if request.user.profile.role == 'ADMIN':
        return redirect('admin_dashboard')
    return redirect('home')