from django.contrib import admin

# Register your models here.
from .models import CustomUser, Region

admin.site.register(CustomUser)
admin.site.register(Region)