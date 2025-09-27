from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import CustomUserManager
# Create your models here.
class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CustomUser(AbstractBaseUser):
    PARENT = "parent"
    STUDENT = "student"
    ROLE_CHOICES = [
        (PARENT, "Parent"),
        (STUDENT, "Student"),
    ]

    MBO = "MBO"
    HBO = "HBO"
    WO = "WO"
    EDUCATION_CHOICES = [
        (MBO, "MBO"),
        (HBO, "HBO"),
        (WO, "WO"),
    ]

    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)

    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    birth_date = models.DateField(null=True, blank=True)  # stores year, month, day
    education_level = models.CharField(max_length=10, choices=EDUCATION_CHOICES, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"  # login with phone
    REQUIRED_FIELDS = ["full_name", "region"]

    def __str__(self):
        return f"{self.full_name}-({self.role})"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser