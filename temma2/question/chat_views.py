from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.shortcuts import get_object_or_404
import json
from rest_framework.permissions import( 
    IsAuthenticated, 
    IsAdminUser, 
    AllowAny
    )
from .models import (
    Category,
    Question,
    Answer,
    Messages,
    MessageRoom,
    MentorMatchScholier,
    MentorMatchStudent
)
from .serializers import(
    CategoryCreateSerializer,
    QuestionCreateSerializer,
    AnswerCreateSerializer,
    QuestionGetSerializer,
    AnswerGetSerializer,
    QuestionUpdateSerializer,
    MessageSerializer,
    MessageRoomSerializer,
    MentorMatchScholierSerializer,
    MentorMatchStudentSerializer
)
from .helper_functions import email_sender
from users.models import User

class MatchStudentView(APIView):
    pass