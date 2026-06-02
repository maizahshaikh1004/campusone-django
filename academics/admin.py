from django.contrib import admin

from .models import Department, Semester,AcademicClass, Subject, FacultySubject
admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(AcademicClass)
admin.site.register(Subject)
admin.site.register(FacultySubject)