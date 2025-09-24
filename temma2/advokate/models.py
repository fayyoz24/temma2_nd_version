from django.db import models

# Create your models here.

class AdvokateRequest(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    problem = models.TextField()
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.full_name} on {self.problem[:30]}..."