from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from django.shortcuts import get_object_or_404
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import jwt
import threading
from rest_framework.permissions import(
    IsAuthenticated,
    IsAdminUser,
    AllowAny
    )
from collections import defaultdict
from django.db import transaction
import pandas as pd
from .models import (
    Category, Question, Answer,
)
from .serializers import(
    CategoryCreateSerializer, QuestionCreateSerializer,
    AnswerCreateSerializer, QuestionGetSerializer,
    AnswerGetSerializer, QuestionUpdateSerializer,
    AnswerCategorySerializer,
    QuestionAllGetSerializer
)
from django.http import JsonResponse
from .helper_functions import (email_sender, generate_token,
        decode_token,send_email_with_HTML,email_sender_for_admin,
        email_by_template, email_by_template_svg)
from users.models import CustomUser as User
import time
import random
from decouple import config

# from .utils import one_time_link
from temma2.settings import DEBUG
# from users.utils import username_generator

# Create your views here.

class CategoryCreateView(APIView):
    def get_permissions(self):
        # Allow any user to access the GET method
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        # Require authentication for other methods
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get(self, request):
        queryset = Category.objects.all()
        # queryset_sub = Category.objects.filter(type='S')
        # Serialize the queryset
        category_type=request.GET.get('category_relation', None)
        if category_type:
            try:
                queryset = Category.objects.filter(related_to=category_type)
            except:
                return Response({"error": "wrong type category"}, status=400)
        serializer=CategoryCreateSerializer(queryset, many=True)
        # Return the serialized data
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer=CategoryCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
        # Save the validated data
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class CategoryDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser]
    list_ids=[1, 2, 3, 4]
    def delete(self, request, pk):
        if int(pk) in self.list_ids:
            return Response({"detail":"you can not delete as it is main category!"}, status=400)
        try:
            Category.objects.get(id=pk).delete()
            return Response({"detail":"succesfully deleted!"}, status=200)
        except:
            return Response({"detail":"id not found!"}, status=404)

class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        category=request.GET.get('category', None)
        if category:
            queryset=Question.objects.filter(is_enabled=True, categories=category).order_by('-id')
            serializer = QuestionGetSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=200)
        queryset=Question.objects.filter(is_enabled=True).order_by('-id')
        serializer = QuestionGetSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer=QuestionCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
        # Save the validated data
            serializer.save()
            if serializer.validated_data.get('categories')[0].related_to=='B':
                email=config('DUO_EMAIL')
                email_sender(email=email, title="New Question!", body='You have a new question, please go and check it! "\n" https://www.temma.app/duo-questions')
            if serializer.validated_data.get('categories')[0].related_to=='L':
                email=config('LAWYER_EMAIL')
                email_sender(email=email, title="New Question!", body='You have a new question, please go and check it! "\n" https://www.temma.app/duo-questions')

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

from .serializers import QuestionUpdateCategSerializer, QuestionCategoryResponseSerializer

class QuestUpdateCreateCategView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = QuestionUpdateCategSerializer

    def get(self, request, id):

        question = get_object_or_404(Question, id=id)

        response_serializer = QuestionCategoryResponseSerializer(question)

        return Response({
            'data': response_serializer.data,
        }, status=200)

    def post(self, request, id):
        input_serializer = self.serializer_class(data=request.data)

        try:
            if input_serializer.is_valid():
                categ_name = input_serializer.validated_data['categ_name']
                quest_id = id
                # get rel question
                question = get_object_or_404(Question, id=quest_id)
                related_to = question.categories.first().related_to
                print(related_to)
                # Get or create category
                category, created = Category.objects.get_or_create(
                    name=categ_name.strip(),
                    defaults={
                        'user': request.user,
                        'related_to': related_to
                    }
                )

                # add category
                question.categories.add(category.id)

                # Serialize response
                response_serializer = QuestionCategoryResponseSerializer(question)

                return Response({
                    'data': response_serializer.data,
                    'new_category': {
                        'id': category.id,
                        'name': category.name,
                        'created': created
                    }
                }, status=201 if created else 200)

            return Response(
                input_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QuestionUpdateListView(APIView):
    permission_classes=[IsAdminUser]
    serializer = QuestionGetSerializer
    def get(self, request):
        # category=request.GET.get('category', None)
        user = request.user
        if user.user_type == 'A':
            queryset=Question.objects.filter(is_enabled=False).order_by('-id')
            serializer=self.serializer(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=200)

        category = user.user_type
        category=Category.objects.filter(related_to=category).first().id
        queryset=Question.objects.filter(is_enabled=False, categories=category).order_by('-id')
        serializer=self.serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)


class AllApprovedQuestionsView(generics.ListAPIView):
    serializer_class = QuestionGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(is_enabled=True).order_by('-id')


class MyQuestionsView(generics.ListAPIView):
    serializer_class = QuestionGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Use self.request instead of taking request as a parameter
        return Question.objects.filter(user=self.request.user)

class HistoryView(APIView):
    serializer_class=QuestionGetSerializer
    permission_classes=[IsAdminUser]

    def get(self, request):
        if request.user.user_type == "A":
            queryset = Question.objects.filter(is_enabled=True).order_by('-id')
            serializer = self.serializer_class(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=200)

        category = request.user.user_type
        category=Category.objects.filter(related_to=category).first().id
        queryset=Question.objects.filter(is_enabled=True, categories=category).order_by('-id')
        serializer=self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)

class QuestionsView(APIView):
    serializer_class=QuestionGetSerializer
    permission_classes=[IsAdminUser]

    def get(self, request):
        if request.user.user_type == "A":
            queryset = Question.objects.all().order_by('-id')
            serializer = self.serializer_class(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=200)

        category = request.user.user_type
        category=Category.objects.filter(related_to=category).first().id
        queryset=Question.objects.filter(categories=category).order_by('-id')
        serializer = self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)

class QuestionUpdateView(APIView):
    permission_classes=[IsAdminUser]
    serializer = QuestionGetSerializer
    def get(self, request):
        id=request.GET.get('id', None)
        try:
            instance = Question.objects.get(id=id)
            serializer = QuestionUpdateSerializer(instance)
            return Response(serializer.data, status=200)
        except:
            return Response({"error":"id not found"}, status=404)

    def patch(self, request):
        id=request.GET.get('id', None)
        try:
            instance = Question.objects.get(id=id)
            # instance.is_enabled=True
            # instance.save()
            serializer = QuestionUpdateSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({"error": "Question not Found", "error1":str(e)}, status=400)

    def delete(self, request):
        id=request.GET.get('id', None)
        try:
            instance = Question.objects.get(id=id)
            instance.delete()
            return Response({"message": "succesfully deleted"},status=200)
        except:
            return Response({"error": "Question not Found"}, status=400)


class AnswerCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get(self, request):
        question_id = request.GET.get('id', None)
        if not question_id:
            return Response({"error": "question id required"}, status=400)
            
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=404)
            
        queryset = Answer.objects.filter(question=question)
        
        # Mark answers as read for the current user if they're authenticated
        current_user = request.user
        if current_user.is_authenticated:
            for answer in queryset:
                # Add the current user to read_by if not already there
                if not answer.is_read_by(current_user):
                    answer.read_by.add(current_user)
        
        # Prepare data for serialization
        serializer = AnswerGetSerializer(queryset, many=True, context={'request': request})
        
        # Add is_answered status to the response
        response_data = {
            'answers': serializer.data,
            'is_answered': question.is_answered,
        }
        
        return Response(response_data, status=200)
    def post(self, request):
        question_id=request.GET.get('id', None)
        try:
            question=Question.objects.get(id=question_id)
            question.is_enabled=True
            question.save()

            email = question.email
            email=question.email
            if not email:
                email = question.user.email
        except Exception as e:
            print(e)
            return Response({"error":"Question not found"}, status=400)
        serializer=AnswerCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.validated_data['question']=question
            serializer.save()
            if not question.is_anonymous:
                email_sender(title="BAAANG!", body="Your question is answered", email=email)
            # Return the serialized data with a 201 Created status code
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AnswerCategoryView(APIView):
    def get(self, request):
        question=request.GET.get('id', None)
        if question:
            queryset = Answer.objects.filter(question=question).prefetch_related('question__categories')

            serialized_categories = CategoryModelSerializer(queryset[0].question.categories.all(), many=True).data
            return JsonResponse({"data":serialized_categories}, status=200)
        return Response({"error":"question id required"}, status=400)


class AnswerCategoryView(APIView):
    def get(self, request):
        question=request.GET.get('id', None)
        if question:
            queryset = Answer.objects.filter(question=question).prefetch_related('question__categories')
            # queryset[0].question.categories
            # serializer=AnswerCategorySerializer(queryset, many=True)
            serialized_categories = CategoryModelSerializer(queryset[0].question.categories.all(), many=True).data
            return JsonResponse({"data":serialized_categories}, status=200)
        return Response({"error":"question id required"}, status=400)


class AnswerUpdateView(APIView):
    permission_classes=[IsAdminUser]
    def patch(self, request):
        id=request.GET.get('id', None)
        try:
            instance = Answer.objects.get(id=id)
        except:
            return Response({"error":"Answer not found"}, status=400)
        serializer = AnswerGetSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            try:
                question = Question.objects.get(title=instance.question)
                email = question.email
                if not email:
                    email = question.user.email
                if not question.is_anonymous:
                    email_sender(title="BAANG!", body="your question's answer is updated", email=email)
            except:
                pass
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            id=request.GET.get('id', None)
            instance = Answer.objects.get(id=id)
            instance.delete()
            return Response(status=200)
        except:
            return Response({"error":"Answer not found"}, status=400)

class HistoryView(APIView):
    serializer_class=QuestionGetSerializer
    permission_classes=[IsAdminUser]

    def get(self, request):
        if request.user.user_type == "A":
            queryset = Question.objects.filter(is_enabled=True).order_by('-id')
            serializer = self.serializer_class(queryset, many=True, context={'request': request})
            return Response(serializer.data, status=200)

        category = request.user.user_type
        category=Category.objects.filter(related_to=category).first().id
        queryset=Question.objects.filter(is_enabled=True, categories=category).order_by('-id')
        serializer=self.serializer_class(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=200)

@csrf_exempt
@api_view(['GET', "POST"])
def update_quest(request, pk):
    try:
        obj = Question.objects.get(pk=pk)
    except Question.DoesNotExist:
        return Response({'error': 'Object not found'}, status=404)

    if request.method=="GET":
        serializer=QuestionGetSerializer(obj, context={'request': request})
        return Response({"data":serializer.data}, status=200)
    try:
        data = request.data
        array_values = data.get('array', [])
        array_values=json.loads(array_values)
        for id in array_values:
            obj.categories.add(id)
        obj.save()
    except:
        return Response({'error': 'Category Not Found with given ID'}, status=404)

    return Response({'success': 'Question updated successfully'}, status=200)


