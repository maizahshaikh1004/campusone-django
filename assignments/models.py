from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
class Assignment(models.Model):
    faculty_subject=models.ForeignKey("academics.FacultySubject",on_delete=models.PROTECT)
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    due_date=models.DateField()
    question_file=models.FileField(upload_to="assignment_questions/", blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=["-created_at"]

    def clean(self):
        if self.pk is None and self.due_date < date.today():
            raise ValidationError("Due date cannot be in the past.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class AssignmentSubmission(models.Model):
    assignment=models.ForeignKey(Assignment,on_delete=models.CASCADE)
    student=models.ForeignKey("users.Profile",on_delete=models.PROTECT)
    submission_file=models.FileField(upload_to="assignment_submissions/")
    submitted_at=models.DateField(auto_now_add=True)

    class Meta:
        unique_together=("assignment","student")

        ordering=["-submitted_at"]

    def clean(self):
        if self.student.role != "STUDENT":
            raise ValidationError("Only students can submit assignments.")

        assignment_class=(self.assignment.faculty_subject.subject.academic_class)
        if self.student.academic_class != assignment_class:
            raise ValidationError("Student does not belong to this class.")

    @property
    def is_late(self):
        if not self.submitted_at:
            return False
            
        return(
            self.submitted_at > self.assignment.due_date
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"{self.student} - {self.assignment.title}")

    