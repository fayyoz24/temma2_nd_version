from django.db import models
from users.models import CustomUser as User
from django.utils import timezone


class Author(models.Model):

    name = models.CharField(max_length=200)
    prof_pic = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Language(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)  # e.g., 'en', 'es', 'fr'

    def __str__(self):
        return self.name 
      
class NewsArticle(models.Model):

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    # title = models.CharField(max_length=200)
    # content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    scheduled_for = models.DateTimeField(null=True, blank=True)  # When the article should become visible
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    website_link = models.URLField(null=True, blank=True)

    original_language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name='original_articles',null=True, blank=True
    )
    original_title = models.CharField(max_length=200)
    original_content = models.TextField()

    def save(self, *args, **kwargs):
        # Set scheduled_for to the current time if it’s not provided
        if self.scheduled_for is None:
            self.scheduled_for = timezone.now()
        super().save(*args, **kwargs)

    def is_published(self):
        return timezone.now() >= self.scheduled_for
    
    def __str__(self):
        return self.author.name + " + " + self.original_title[:50]


    def get_version(self, language_code, difficulty='medium'):
        try:
            return self.versions.get(
                language__code=language_code,
                difficulty_level=difficulty
            )
        except ArticleVersion.DoesNotExist:
            return None

class ArticleVersion(models.Model):
    """Different versions of the article (combinations of language and difficulty)"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('super_easy', 'Super-easy'),
        ('medium', 'Medium'),
    ]

    article = models.ForeignKey(
        NewsArticle,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE
    )
    difficulty_level = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()

    class Meta:
        unique_together = ['article', 'language', 'difficulty_level']
        indexes = [
            models.Index(fields=['language', 'difficulty_level']),
        ]

    def __str__(self):
        return f"{self.title} ({self.language.code} - {self.difficulty_level})"

class UserNewsView(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        self.article.original_title
    