from django.urls import path, include
from .views import(
    CategoryCreateView, CategoryDeleteView,
    QuestionCreateView, QuestionUpdateView, QuestionUpdateListView,update_quest,
    AnswerCreateView, AnswerUpdateView, AnswerCategoryView,
    HistoryView, MyInbox,
    
    MessageRoomCreate,
    MentormatchStudentView, MentormatchScholierView,
    # MentormatchScholierViewList,
    # MentormatchStudentViewList,
    # MentormatchScholierUpdateView,
    # MentormatchStudentUpdateView,
    OneTimeLinkForMentorView,
    MentorForScholierView, 
    MentorForStudentView,MentorTest,
    StudiesListView, UniversitiesListView,
    UnsubscribeView, #MentormatchScholierTestView, MentorForScholierTestView,
    PopularStudiesView, AllStudiesWithInformationView,
    SendEmailNewMentor,JobTitleView, SectorView,
    QuestionsView,
    #test
    UniversityView, StudyView,
    QuestUpdateCreateCategView,
    MentorForReRunView, MyQuestionsView
)
from .view_test import StudentAdd, RerunSystem, RerunMentor

from users.views import UserDetailView, PassCodeGroupsView

urlpatterns = [
    # users
    path('user-detail', UserDetailView.as_view(), name='user-detail'),
    path('pass-code', PassCodeGroupsView.as_view(), name='pass-code'),
    path('rerun-system', RerunSystem.as_view(), name='rerun-system'),


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
    path('chat', MyInbox.as_view(), name='MyInbox'),
    path('room', MessageRoomCreate.as_view(), name='room'),
    path('update-quest/<int:pk>', update_quest, name='update_quest'),

    path('one-time-link', OneTimeLinkForMentorView.as_view(), name='one-time-link'),
    
    path('mentor-match-student', MentormatchStudentView.as_view(), name='mentor-match-student'),
    path('mentor-match-scholier', MentormatchScholierView.as_view(), name='mentor-match-scholier'),
    # path('mentor-for-scholier-test', MentorForScholierTestView.as_view(), name='mentor-match-scholier'),
    # path('mentor-match-scholier-list', MentormatchScholierViewList.as_view(), name='mentor-match-scholier-list'),
    # path('mentor-match-student-list', MentormatchStudentViewList.as_view(), name='mentor-match-student-list'),
    # path('mentor-match-scholier-update/<int:pk>', MentormatchScholierUpdateView.as_view(), name='mentor-match-scholier-update'),
    # path('mentor-match-student-update/<int:pk>', MentormatchStudentUpdateView.as_view(), name='mentor-match-student-update'),

    # path('job-titles', JobTitleView.as_view(), name='job-titles'),
    path('sectors', SectorView.as_view(), name='sectors'),
    path('sectors/<int:pk>', JobTitleView.as_view(), name='job-titles'),

    path('mentor-for-student', MentorForStudentView.as_view(), name='mentor-for-student'),
    path('mentor-for-scholier', MentorForScholierView.as_view(), name='mentor-for-scholier'),

    
    path('student-add', StudentAdd.as_view(), name='student-add'),
    path('rerun-mentor', RerunMentor.as_view(), name='rerun-mentor'),
    path('mentor-test', MentorTest.as_view(), name='mentor-test'),


    path('unsubscribe', UnsubscribeView.as_view(), name='unsubscribe'),
    path('universities', UniversityView.as_view(), name='universities'),
    path('studies', StudyView.as_view(), name='studies'),
    path('studies-list', StudiesListView.as_view(), name='studies-list'),
    path('universities-list', UniversitiesListView.as_view(), name='universities-list'),
    path('popular-studies', PopularStudiesView.as_view(), name='popular-studies'),
    path('all-studies-with-informations', AllStudiesWithInformationView.as_view(), name='all-studies'),
    path('send-email-once-week', SendEmailNewMentor.as_view(), name='send-email-once-week'),
    path('mentor-rerun', MentorForReRunView.as_view(), name='mentor-rerun'),
]