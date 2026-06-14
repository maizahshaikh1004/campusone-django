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

class AttendanceCorrectionRequest(models.Model):
    STATUS_CHOICES=(
        ("PENDING","Pending"),
        ("APPROVED","Approved"),
        ("REJECTED","Rejected")
    )
    attendance_record=models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE)
    faculty=models.ForeignKey("users.Profile",on_delete=models.PROTECT)
    reason=models.TextField()
    requested_is_present=models.BooleanField()
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    admin_remark=models.TextField(blank=True)
    requested_at=models.DateTimeField(auto_now_add=True)
    reviewed_at=models.DateTimeField(blank=True,null=True)

    def clean(self):
        if self.faculty.role!="FACULTY":
            raise ValidationError("Only faculty can raise attendance correction requests.")

        attendance_faculty=(
            self.attendance_record.attendance_session.timetable.faculty_subject.faculty
            )
        if self.faculty != attendance_faculty:
            raise ValidationError("Faculty can only request corrections for their own attendance records.")

        if self.attendance_record.is_present == self.requested_is_present:
            raise ValidationError("Requested Status must be different from Current attendance status.")
        
        existing_request = (
    AttendanceCorrectionRequest.objects.filter(
        attendance_record=self.attendance_record,
        status="PENDING"
    ).exclude(pk=self.pk))

        if existing_request.exists():
            raise ValidationError(
        "A pending correction request already exists."
    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
        f"{self.attendance_record.student} - "
        f"{self.status}"
    )


class Notice(models.Model):
    NOTICE_TYPE_CHOICES=(
        ("GENERAL","General"),
        ("DEPARTMENT","Department"),
        ("CLASS","Class")
    )   
    title=models.CharField(max_length=200)
    content=models.TextField(blank=True)
    created_by=models.ForeignKey("users.Profile",on_delete=models.PROTECT)
    notice_type=models.CharField(max_length=20,choices=NOTICE_TYPE_CHOICES)
    department=models.ForeignKey(Department, on_delete=models.PROTECT, blank=True,null=True)
    academic_class=models.ForeignKey(AcademicClass,on_delete=models.PROTECT, blank=True,null=True)
    attachment=models.FileField(upload_to="notices/", blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.notice_type=="GENERAL":
            self.department=None  
            self.academic_class=None
        
        elif self.notice_type=="DEPARTMENT":
            if self.department is None:
                raise ValidationError("Department notice must have a department.")
            
            self.academic_class=None
        
        elif self.notice_type=="CLASS":
            if self.academic_class is None:
                raise ValidationError("Class notice must have an academic class.")
            
            self.department=None

        if self.created_by.role not in ["ADMIN","FACULTY"]:
            raise ValidationError("Only Admin or Faculty can create notices.")

        if not self.content and not self.attachment:
            raise ValidationError("Notice must contain content or an attachment.")

        if self.created_by.role == "FACULTY":
            faculty_department= self.created_by.department
            if self.notice_type=="DEPARTMENT":
                if self.department!=faculty_department:
                    raise ValidationError("Faculty can only create department notices for their own department.")
                
            elif self.notice_type=="CLASS":
                if (self.academic_class.department != faculty_department):
                    raise ValidationError("Faculty can only create class notices for classes in their own department.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)       

    def __str__(self):
        return self.title

class Event(models.Model):
    EVENT_TYPE_CHOICES=(
        ("GENERAL","General"),
        ("DEPARTMENT","Department"),
        ("CLASS","Class")
    )   
    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    event_type=models.CharField(max_length=20,choices=EVENT_TYPE_CHOICES)
    department=models.ForeignKey(Department, on_delete=models.PROTECT, null=True,blank=True)
    academic_class=models.ForeignKey(AcademicClass, on_delete=models.PROTECT,null=True,blank=True)
    event_date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    venue=models.CharField(max_length=100)
    poster=models.FileField(upload_to="events/", blank=True, null=True)
    google_form_link=models.URLField(blank=True)
    created_by=models.ForeignKey("users.Profile",on_delete=models.PROTECT,related_name="created_events")
    faculty_incharge = models.ForeignKey(
        "users.Profile",
        on_delete=models.PROTECT,
        related_name="managed_events"
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def clean(self):
        if self.event_type=="GENERAL":
            self.department=None  
            self.academic_class=None
        elif self.event_type=="DEPARTMENT":
            if self.department is None:
                raise ValidationError("Department event must have a department.")
            self.academic_class=None
        elif self.event_type=="CLASS":
            if self.academic_class is None:
                raise ValidationError("Class event must have a class.")
            self.department=None
        
        if self.created_by.role not in ["ADMIN","FACULTY"]:
            raise ValidationError("Only admin and faculty can create the event.")

        if self.created_by.role == "FACULTY":
            faculty_department= self.created_by.department
            if self.event_type=="DEPARTMENT":
                if self.department!=faculty_department:
                    raise ValidationError("Faculty can only create department events for their own department.")
                
            elif self.event_type=="CLASS":
                if (self.academic_class.department != faculty_department):
                    raise ValidationError("Faculty can only create class events for classes in their own department.")
        
        if self.faculty_incharge.role != "FACULTY":
            raise ValidationError("Faculty Incharge must have FACULTY role.")

        if self.start_time>=self.end_time:
            raise ValidationError("End time must be after start time.")
        
        if self.event_date<=date.today():
            raise ValidationError("Event date must be in the future.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)       

    def __str__(self):
        return self.title
           
class EventCoordinator(models.Model):
    event=models.ForeignKey(Event, on_delete=models.CASCADE)
    student=models.ForeignKey("users.Profile", on_delete=models.PROTECT)

    def clean(self):
        if self.student.role != "STUDENT":
            raise ValidationError("Only students can be event coordinators.")
        
        existing_coordinators =(
            EventCoordinator.objects.filter(event=self.event).exclude(pk=self.pk)
            ) 
        if existing_coordinators.count() >= 2:
            raise ValidationError("Maximum 2 coordinators are allowed per event.")
        # GENERAL events: any student can be coordinator
        if self.event.event_type == "DEPARTMENT":
            if self.student.academic_class.department != self.event.department:
                raise ValidationError("Coordinator must belong to the event department.")
        
        if self.event.event_type == "CLASS":
            event_department = (self.event.academic_class.department)
            if (self.student.academic_class.department!= event_department ):
                raise ValidationError(
            "Coordinator must belong to the event department."
        )
    class Meta:
        unique_together = (
        "event",
        "student"
    )
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.student} - {self.event}"
    


    

    

        