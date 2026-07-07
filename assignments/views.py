from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Assignment, AssignmentSubmission
from django.http import HttpResponse
from django.contrib import messages
from academics.models import FacultySubject
from django.core.exceptions import ValidationError
from datetime import date
from users.models import Profile


@login_required
def student_assignments(request):

    profile = request.user.profile

    if profile.role != "STUDENT":
        return render(
            request,
            "403.html",
            {"message": "Students Only."},
            status=403
        )

    assignments = (
        Assignment.objects.filter(
            faculty_subject__subject__academic_class=profile.academic_class
        )
        .select_related(
            "faculty_subject",
            "faculty_subject__subject",
            "faculty_subject__faculty"
        )
        .order_by("due_date")
    )

    assignment_data = []

    for assignment in assignments:

        submission = AssignmentSubmission.objects.filter(
            assignment=assignment,
            student=profile
        ).first()

        assignment_data.append({
            "assignment": assignment,
            "submission": submission,
            "is_submitted": submission is not None,
        })

    return render(
        request,
        "student/student_assignments.html",
        {
            "assignment_data": assignment_data,
        }
    )

@login_required
def submit_assignment(request, assignment_id):

    profile = request.user.profile

    assignment = get_object_or_404(
        Assignment,
        pk=assignment_id
    )

    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=profile
    ).first()

    if request.method == "POST" and submission is None:
        try:
            AssignmentSubmission.objects.create(
                assignment=assignment,
                student=profile,
                submission_file=request.FILES["submission_file"]
            )
            messages.success(request, "Assignment submitted successfully.")
            return redirect(
                "student_assignments"
            )
        except ValidationError as e:
            messages.error(request, e.messages[0] if hasattr(e, 'messages') else str(e))

    return render(
        request,
        "student/student_submit_assignment.html",
        {
            "assignment": assignment,
            "submission": submission,
        }
    )

@login_required
def faculty_assignments(request):

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

    assignments = (
        Assignment.objects.filter(
            faculty_subject__faculty=profile
        )
        .select_related(
            "faculty_subject",
            "faculty_subject__subject",
            "faculty_subject__subject__academic_class"
        )
        .order_by("due_date")
    )

    return render(
        request,
        "faculty/faculty_assignments.html",
        {
            "assignments": assignments,
        }
    )


@login_required
def create_assignment(request):

    profile = request.user.profile

    if profile.role != "FACULTY":
        return render(
            request,
            "403.html",
            {"message": "Faculty Only."},
            status=403
        )

    faculty_subjects = (
        FacultySubject.objects.filter(
            faculty=profile
        )
        .select_related(
            "subject",
            "subject__academic_class"
        )
        .order_by(
            "subject__name"
        )
    )

    if request.method == "POST":

        faculty_subject = get_object_or_404(
            FacultySubject,
            id=request.POST.get("faculty_subject"),
            faculty=profile
        )

        try:
            Assignment.objects.create(
                faculty_subject=faculty_subject,
                title=request.POST.get("title"),
                description=request.POST.get("description"),
                due_date=request.POST.get("due_date"),
                question_file=request.FILES.get("question_file")
            )
            messages.success(
                request,
                "Assignment created successfully."
            )
            return redirect("faculty_assignments")
        except ValidationError as e:
            messages.error(request, e.messages[0] if hasattr(e, 'messages') else str(e))

    return render(
        request,
        "faculty/create_assignment.html",
        {
            "faculty_subjects": faculty_subjects
        }
    )


@login_required
def edit_assignment(request, assignment_id):

    profile = request.user.profile

    if profile.role != "FACULTY":
        return render(
            request,
            "403.html",
            {"message": "Faculty Only."},
            status=403
        )

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        faculty_subject__faculty=profile
    )

    faculty_subjects = FacultySubject.objects.filter(
        faculty=profile
    ).select_related(
        "subject",
        "subject__academic_class"
    )

    if request.method == "POST":

        assignment.faculty_subject = get_object_or_404(
            FacultySubject,
            id=request.POST.get("faculty_subject"),
            faculty=profile
        )

        assignment.title = request.POST.get("title")
        assignment.description = request.POST.get("description")
        assignment.due_date = request.POST.get("due_date")

        if request.FILES.get("question_file"):
            assignment.question_file = request.FILES["question_file"]

        try:
            assignment.full_clean()
            assignment.save()

            messages.success(
                request,
                "Assignment updated successfully."
            )

            return redirect("faculty_assignments")

        except ValidationError as e:

            messages.error(
                request,
                e.messages[0]
            )

    return render(
        request,
        "faculty/edit_assignment.html",
        {
            "assignment": assignment,
            "faculty_subjects": faculty_subjects,
            "today": date.today(),
        }
    )


@login_required
def delete_assignment(request, assignment_id):

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

    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        faculty_subject__faculty=profile
    )

    if request.method == "POST":

        assignment.delete()

        messages.success(
            request,
            "Assignment deleted successfully."
        )

        return redirect("faculty_assignments")

    return render(
        request,
        "faculty/delete_assignment.html",
        {
            "assignment": assignment
        }
    )


@login_required
def faculty_submissions(request):
    profile = request.user.profile
    if profile.role != 'FACULTY':
        return render(request, '403.html', {'message': 'Faculty Only.'}, status=403)

    selected_assignment_id = request.GET.get('assignment_id')
    
    assignments_qs = Assignment.objects.filter(
        faculty_subject__faculty=profile
    ).select_related('faculty_subject__subject').order_by('-due_date')

    submissions_qs = []
    pending_students_qs = []
    total_students = 0

    if selected_assignment_id:
        assignment = get_object_or_404(Assignment, id=selected_assignment_id, faculty_subject__faculty=profile)
        class_students = Profile.objects.filter(
            role='STUDENT',
            academic_class=assignment.faculty_subject.subject.academic_class,
            user__is_active=True
        ).order_by('full_name')

        submissions_qs = AssignmentSubmission.objects.filter(
            assignment=assignment
        ).select_related('student')

        submitted_student_ids = submissions_qs.values_list('student_id', flat=True)
        pending_students_qs = class_students.exclude(id__in=submitted_student_ids)
        total_students = class_students.count()

    return render(request, 'faculty/faculty_assignment_submissions.html', {
        'assignments': assignments_qs,
        'submissions': submissions_qs,
        'pending_students': pending_students_qs,
        'selected_assignment_id': selected_assignment_id,
        'total_students': total_students
    })