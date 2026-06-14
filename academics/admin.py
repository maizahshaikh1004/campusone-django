from django.contrib import admin

from .models import Department, Semester,AcademicClass, Subject, FacultySubject, Timetable, AttendanceSession, AttendanceRecord,AttendanceCorrectionRequest
from .models import Notice, Event
admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(AcademicClass)
admin.site.register(Subject)
admin.site.register(FacultySubject)
admin.site.register(Timetable)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
admin.site.register(AttendanceCorrectionRequest)
admin.site.register(Notice)
admin.site.register(Event)