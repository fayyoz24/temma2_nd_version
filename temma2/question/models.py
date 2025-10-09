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
