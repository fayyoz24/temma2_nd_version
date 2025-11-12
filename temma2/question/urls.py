from django.urls import path, include
from .views import(
    CategoryCreateView, 
    CategoryDeleteView,
    QuestionCreateView, 
    QuestionUpdateView, 
    QuestionUpdateListView,
    update_quest,
    AnswerCreateView, 
    AnswerUpdateView, 
    AnswerCategoryView,
    HistoryView, 
    QuestionsView,
    QuestUpdateCreateCategView,
    MyQuestionsView,
    AllApprovedQuestionsView
)

urlpatterns = [
    path('categ-create', CategoryCreateView.as_view(), name='categ-create'),
    path('categ-delete/<int:pk>', CategoryDeleteView.as_view(), name='categ-delete/<int:pk>'),
    path('quest-create', QuestionCreateView.as_view(), name='quest-create'),
    path('quest-history', HistoryView.as_view(), name='quest-history'),
    path('quest-update-categ/<int:id>', QuestUpdateCreateCategView.as_view(), name='quest-update-categ'),
    path('answer-create', AnswerCreateView.as_view(), name='answer-create'),
    path('answer-category', AnswerCategoryView.as_view(), name='answer-category'),
    path('answer-update', AnswerUpdateView.as_view(), name='answer-update'),
    path('questions', QuestionsView.as_view(), name='questions'),
    path('my-questions', MyQuestionsView.as_view(), name='my-questions'),
    path('quest-update', QuestionUpdateView.as_view(), name='quest-update'),
    path('quest-update-list', QuestionUpdateListView.as_view(), name='quest-update-list'),
    path('questions-history', QuestionUpdateView.as_view(), name='questions-history'),
    path('update-quest/<int:pk>', update_quest, name='update_quest'),
    path('all-approved-questions', AllApprovedQuestionsView.as_view(), name='all-approved-questions'),
]