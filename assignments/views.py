from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Assignment, AssignmentSubmission


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

        AssignmentSubmission.objects.create(
            assignment=assignment,
            student=profile,
            submission_file=request.FILES["submission_file"]
        )

        return redirect(
            "student_assignments"
        )

    return render(
        request,
        "student/student_submit_assignment.html",
        {
            "assignment": assignment,
            "submission": submission,
        }
    )