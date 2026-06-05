from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
class Department(models.Model):
    name=models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Semester(models.Model):
    semester_number=models.IntegerField()

    def __str__(self):
        return f"Semester {self.semester_number}"


class AcademicClass(models.Model):
    name=models.CharField(max_length=50)

    department=models.ForeignKey(Department, on_delete=models.PROTECT)
    semester=models.ForeignKey(Semester, on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name=models.CharField(max_length=100)

    academic_class=models.ForeignKey(AcademicClass, on_delete=models.PROTECT)

    class Meta:
     unique_together = (
        "name",
        "academic_class"
    )

    def __str__(self):
        return self.name

class FacultySubject(models.Model):
    faculty=models.ForeignKey("users.Profile", on_delete=models.PROTECT)
    subject=models.ForeignKey(Subject,on_delete=models.PROTECT)

    def clean(self):
        if self.faculty.role !="FACULTY":
            raise ValidationError("Selected profile must have FACULTY role") 

        faculty_department=self.faculty.department
        subject_department=self.subject.academic_class.department

        if faculty_department != subject_department:
            raise ValidationError("Faculty and Subject MUST belong to the same Department.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.faculty} - {self.subject}"


class Timetable(models.Model):
    DAY_CHOICES=[
        ("MONDAY","Monday"),
        ("TUESDAY","Tuesday"),
        ("WEDNESDAY","Wednesday"),
        ("THURSDAY","Thursday"),
        ("FRIDAY","Friday"),
        ("SATURDAY","Saturday"),
    ]
    faculty_subject=models.ForeignKey(FacultySubject, on_delete=models.PROTECT)

    day=models.CharField(max_length=10,choices=DAY_CHOICES)
    start_time=models.TimeField()
    end_time=models.TimeField()

    def clean(self):
        if self.start_time>=self.end_time:
            raise ValidationError("End time must be after Start time.")

        faculty = self.faculty_subject.faculty

        academic_class = (
        self.faculty_subject
        .subject
        .academic_class
    )

        existing_entries = Timetable.objects.filter(
        day=self.day
    ).exclude(pk=self.pk)

        for entry in existing_entries:

            overlap = (
            self.start_time < entry.end_time
            and self.end_time > entry.start_time
        )

            if not overlap:
                continue

        # Faculty overlap
            if (
            entry.faculty_subject.faculty
            == faculty
        ):
                raise ValidationError(
                "Faculty already has a lecture during this time."
            )

        # Class overlap
            entry_class = (
            entry.faculty_subject
            .subject
            .academic_class
        )

            if entry_class == academic_class:
                raise ValidationError(
                "This class already has a lecture during this time."
            )

    def __str__(self):
        return (
            f"{self.faculty_subject} "
            f"on {self.day} "
            f"from {self.start_time} - {self.end_time}"
        )

class AttendanceSession(models.Model):
    timetable=models.ForeignKey(Timetable, on_delete=models.PROTECT)
    lecture_date=models.DateField()
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=("timetable","lecture_date")

    def clean(self):
        if self.lecture_date> date.today():
            raise ValidationError("Attendance cannot be marked for future dates.")

    
    
    def __str__(self):
        return f"{self.timetable} - {self.lecture_date}"


class AttendanceRecord(models.Model):
    attendance_session=models.ForeignKey(AttendanceSession,on_delete=models.CASCADE)
    student=models.ForeignKey("users.Profile",on_delete=models.PROTECT)
    is_present=models.BooleanField()

    class Meta:
        unique_together = (
        "attendance_session",
        "student"
    )
    def clean(self):
        if self.student.role !="STUDENT":
            raise ValidationError("Attendance can only be marked for Students.")

        attendance_class = (
        self.attendance_session
        .timetable
        .faculty_subject
        .subject
        .academic_class
    )
        if self.student.academic_class != attendance_class:
            raise ValidationError(
            "Student does not belong to this class."
        )

    

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.student} - "
            f"{'Present' if self.is_present else 'Absent'}"
        )

    