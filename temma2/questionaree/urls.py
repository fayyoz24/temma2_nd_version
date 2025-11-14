from .views import AllQuestionsView
from django.urls import path

urlpatterns = [
    path("questions/", AllQuestionsView.as_view(), name="all-questions")
]