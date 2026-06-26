from django.db import models
from django.contrib.auth.models import User
from academics.models import AcademicClass, Department
from django.core.exceptions import ValidationError

# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES=(
        ('ADMIN','Admin'),
        ('FACULTY','Faculty'),
        ('STUDENT','Student')
    )

    user=models.OneToOneField(User,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=100,default="")
    role=models.CharField(max_length=20,choices=ROLE_CHOICES)
    department = models.ForeignKey(
    Department,
    on_delete=models.PROTECT,
    null=True,
    blank=True
)

    academic_class=models.ForeignKey(AcademicClass, on_delete=models.PROTECT, null=True,blank=True)
    phone=models.CharField(max_length=10,blank=True)
    bio=models.TextField(blank=True)
    profile_photo=models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True
    )
    address=models.TextField(blank=True)
    def __str__(self):
        return self.user.username
    
class RegistrationRequest(models.Model):
    ROLE_CHOICES=(
        ('STUDENT','Student'),
        ('FACULTY','Faculty')
    )
    name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=20,choices=ROLE_CHOICES)
    department=models.ForeignKey(Department,on_delete=models.PROTECT)
    academic_class=models.ForeignKey(AcademicClass,on_delete=models.PROTECT,null=True,
    blank=True)
    STATUS_CHOICES=(
        ('PENDING','Pending'),
        ('APPROVED','Approved'),
        ('REJECTED','Rejected')
    )
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="PENDING")
    requested_at = models.DateTimeField(
    auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
    null=True,
    blank=True
    )
    admin_remark = models.TextField(
    blank=True)
    def clean(self):
        if self.role=="FACULTY":
            self.academic_class=None
        if self.role == "STUDENT":
            if self.academic_class is None:
                raise ValidationError(
                    "Students must select an academic class."
                )
            if self.academic_class.department != self.department:
                raise ValidationError(
                    "Selected class does not belong to the selected department."
                )
        existing_request = (RegistrationRequest.objects.filter(
        email=self.email,
        status="PENDING").exclude(pk=self.pk))

        if existing_request.exists():
            raise ValidationError(
                "A pending registration request already exists for this email."
            )
        if self.pk is None:
            if User.objects.filter(email=self.email).exists():
                raise ValidationError(
                    "An account with this email already exists."
                )
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

