from django.db import models
from django.core.exceptions import ValidationError
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

    def __str__(self):
        return self.name

class FacultySubject(models.Model):
    faculty=models.ForeignKey("users.Profile", on_delete=models.PROTECT)
    subject=models.ForeignKey(Subject,on_delete=models.PROTECT)

    def clean(self):
        if self.faculty.role !="FACULTY":
            raise ValidationError("Selected profile must have FACULTY role") 

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.faculty} - {self.subject}"

