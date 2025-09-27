from django.db import models
from users.models import CustomUser as User
import datetime
# Create your models here.

LAWYER = 'L'
BOOKIE = 'B'
MENTAL_COACH='M'
FAVORITES='F'

CATEGORY_TYPE_CHOICES = [(LAWYER, 'My Lawyer'),
                     (BOOKIE, 'My Bookie'),
                     (MENTAL_COACH, 'My Mental Coach'),
                     (FAVORITES, 'My Favorites')]

STUDENT = 'ST'
SCHOLIER = 'SC'
SENIOR = 'SN'

USER_TYPE_CHOICES = [(STUDENT, 'Student'),
                     (SCHOLIER, 'Scholier')]

DEGREE_TYPE_CHOICES = [(STUDENT, 'Student'),
                     (SENIOR, 'Senior')]
class Category(models.Model):
    user=models.ForeignKey(User, related_name="category_creator", on_delete=models.CASCADE, blank=True)
    name=models.CharField(max_length=100)
    # Default type must be defined to enforce security
    related_to = models.CharField(max_length=1, choices=CATEGORY_TYPE_CHOICES,
                                  verbose_name="Category  relation", default="L")
    date_time = models.DateField(default=datetime.date.today)

    def __str__(self):
        return str(self.name)

class Question(models.Model):
    # Your existing fields remain the same
    user = models.ForeignKey(User, related_name='quest_sender', on_delete=models.DO_NOTHING, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name="question_updated_by", on_delete=models.CASCADE, null=True)
    created_at = models.DateField(default=datetime.date.today)
    last_updated = models.DateField(default=datetime.date.today)
    categories = models.ManyToManyField(Category, related_name="questions")
    title = models.CharField(max_length=100)
    detail = models.TextField()
    is_enabled = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return str(self.title)

    @property
    def is_answered(self):
        """Returns True if the question has at least one answer."""
        return self.answer_set.exists()

class Answer(models.Model):
    # Your existing fields
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answered_by = models.ForeignKey(User, related_name="answered_by", on_delete=models.CASCADE, null=True)
    created_at = models.DateField(default=datetime.date.today)
    updated_by = models.ForeignKey(User, related_name="answer_updated_by", on_delete=models.CASCADE)
    last_updated = models.DateField(default=datetime.date.today)
    detail = models.TextField()
    
    # New field - users who have read this answer
    read_by = models.ManyToManyField(User, related_name="read_answers", blank=True)

    def __str__(self):
        return self.detail
    
    def is_read_by(self, user):
        """Check if a specific user has read this answer"""
        if not user or not user.is_authenticated:
            return False
        return self.read_by.filter(id=user.id).exists()

# chatting
# class Messages(models.Model):
#     room=models.ForeignKey("MessageRoom", on_delete=models.CASCADE, to_field='cookie', null=True)
#     related_to=models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
#     sender=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     text = models.CharField(max_length=1000)
#     is_read = models.BooleanField(default=False)
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.text

# class MessageRoom(models.Model):
#     cookie=models.CharField(max_length=100, unique=True)

#     # def __str__(self):
#     #     return self.id

# BACHELOR = 'B'
# MASTER = 'M'
# UNDEFINED = 'U'
# UNIVERSITY_DEGREE_CHOICES=[(UNDEFINED, 'Undefined'),
#                      (BACHELOR, 'Bachelor'),
#                      (MASTER, 'Master')]

# class University(models.Model):
#     degree = models.CharField(max_length=1, choices=UNIVERSITY_DEGREE_CHOICES, default='U')
#     name = models.CharField(max_length=200)
#     logo = models.CharField(max_length=200, blank=True, null=True)

#     def __str__(self):
#         return self.name

# class Study(models.Model):
#     degree = models.CharField(max_length=1, choices=UNIVERSITY_DEGREE_CHOICES, default='M')
#     university=models.ForeignKey(University, on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=150)

#     def __str__(self):
#         return self.name

# class MentorMatchStudent(models.Model):

#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     job_title=models.ForeignKey("JobTitle", on_delete=models.CASCADE, null=True)
#     email = models.EmailField()
#     is_replied=models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)

#     def __str__(self):
#         return self.user.username

# class MentorMatchScholier(models.Model):

#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     university=models.ForeignKey(University, on_delete=models.CASCADE, null=True)
#     study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True)
#     email = models.EmailField()
#     is_replied=models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)

# class Sector(models.Model):
#     sector=models.CharField(max_length=150)

#     def __str__(self):
#         return self.sector

# class JobTitle(models.Model):

#     job_title = models.CharField(max_length=150)
#     sector = models.ForeignKey(Sector, on_delete=models.CASCADE, null=True, blank=True)

#     def __str__(self):
#         return self.job_title
    
# class MentorForStudent(models.Model):

#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=200)
#     email = models.EmailField()
#     linkedin_link=models.CharField(max_length=200, null=True, blank=True)
#     job_title = models.ForeignKey(JobTitle, on_delete=models.CASCADE, null=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)

#     def __str__(self):
#         return self.name

# class MentorForScholier(models.Model):
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     linkedin_link = models.CharField(max_length=200, null=True, blank=True)
#     study = models.ForeignKey(Study, on_delete=models.CASCADE, null=True)
#     university = models.ForeignKey(University, on_delete=models.CASCADE, null=True)
#     created_at = models.DateTimeField(auto_now_add=True, null=True)

#     def __str__(self):
#         return self.name
