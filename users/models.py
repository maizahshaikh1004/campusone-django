from django.db import models
from django.contrib.auth.models import User
from academics.models import AcademicClass

# Create your models here.
class Profile(models.Model):
    ROLE_CHOICES=(
        ('ADMIN','Admin'),
        ('FACULTY','Faculty'),
        ('STUDENT','Student')
    )

    user=models.OneToOneField(User,on_delete=models.CASCADE)
    role=models.CharField(max_length=20,choices=ROLE_CHOICES)
    academic_class=models.ForeignKey(AcademicClass, on_delete=models.PROTECT, null=True,blank=True)
    phone=models.CharField(max_length=10,blank=True)
    bio=models.TextField(blank=True)
    profile_photo=models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True
    )
    def __str__(self):
        return self.user.username
    