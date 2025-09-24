from django.contrib import admin
from .models import (NewsArticle, 
                     UserNewsView, 
                     Author,
                    ArticleVersion,
                    Language)
# Register your models here.
admin.site.register(NewsArticle)
admin.site.register(UserNewsView)
admin.site.register(Author)
# admin.site.register(ArticleVersion)
admin.site.register(Language)



# class ArticleVersion(models.Model):
#     """Different versions of the article (combinations of language and difficulty)"""
#     DIFFICULTY_CHOICES = [
#         ('easy', 'Easy'),
#         ('super_easy', 'Super-easy'),
#         ('medium', 'Medium'),
#     ]

#     article = models.ForeignKey(
#         NewsArticle,
#         on_delete=models.CASCADE,
#         related_name='versions'
#     )
#     language = models.ForeignKey(
#         Language,
#         on_delete=models.CASCADE
#     )
#     difficulty_level = models.CharField(
#         max_length=10,
#         choices=DIFFICULTY_CHOICES,
#         default='medium'
#     )
#     title = models.CharField(max_length=200)
#     content = models.TextField()

#     class Meta:
#         unique_together = ['article', 'language', 'difficulty_level']
#         indexes = [
#             models.Index(fields=['language', 'difficulty_level']),
#         ]

#     def __str__(self):
#         return f"{self.title} ({self.language.code} - {self.difficulty_level})"

class ArticleVersionAdmin(admin.ModelAdmin):
    list_display = ['author', 'difficulty_level', 'language', 'article']
    search_fields = ['article__author__name', 'article__original_title']
    ordering = ['article__author__name', 'difficulty_level']
    
    @admin.display(description='article', ordering='article__original_title')
    def article(self, object):
        return object.article.original_title[:50]
    
    @admin.display(description='author', ordering='article__author__name')
    def author(self, object):
        return object.article.author.name
    
admin.site.register(ArticleVersion, ArticleVersionAdmin)
    