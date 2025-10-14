from django.db import models

# Create your models here.

class AdvokateRequest(models.Model):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    problem = models.TextField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_name = self.user.full_name if self.user and self.user.full_name else "Unnamed user"
        problem_preview = self.problem[:30].replace("\n", " ")  # tozalash uchun
        return f"Request by {user_name} on {problem_preview}..."