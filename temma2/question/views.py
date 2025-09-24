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
from chatting.models import Room
from .models import (
    Category, Question, Answer,
    Messages, MessageRoom,
    MentorForScholier,  MentorForStudent,
    MentorMatchScholier,
    MentorMatchStudent, Sector,
    University, Study, JobTitle#MentorForScholierTest, MentorMatchScholierTest
)
from .serializers import(
    CategoryCreateSerializer, QuestionCreateSerializer,
    AnswerCreateSerializer, QuestionGetSerializer,
    AnswerGetSerializer, QuestionUpdateSerializer,
    MessageSerializer,  MessageRoomSerializer,
    MentorForScholierSerializer, MentorForStudentSerializer,
    MentorMatchStudentSerializer, MentorMatchScholierSerializer,
    AnswerCategorySerializer,
    CategoryModelSerializer, UniversitySerializer,
    StudySerializer, SectorSerializer, QuestionAllGetSerializer
)
from chatting.serializers import JobTitleSerializer
from django.http import JsonResponse
from .helper_functions import (email_sender, generate_token,
        decode_token,send_email_with_HTML,email_sender_for_admin,
        email_by_template, email_by_template_svg)
from users.models import User
import time
import random
from decouple import config

from .utils import one_time_link
from temma.settings import DEBUG
from users.utils import username_generator

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
                email_sender(email=email, title="New Question!", body='You have a new question, please go and check it! "\n" https://temma.app/pending-questions')
            if serializer.validated_data.get('categories')[0].related_to=='L':
                email=config('LAWYER_EMAIL')
                email_sender(email=email, title="New Question!", body='You have a new question, please go and check it! "\n" https://temma.app/pending-questions')

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

# class AnswerCreateView(APIView):
#     def get_permissions(self):
#         # Allow any user to access the GET method
#         if self.request.method == 'GET':
#             self.permission_classes = [AllowAny]
#         # Require authentication for other methods
#         else:
#             self.permission_classes = [IsAdminUser]
#         return super().get_permissions()

#     def get(self, request):
#         question=request.GET.get('id', None)
#         if question:
#             queryset=Answer.objects.filter(question=question)
#             serializer=AnswerGetSerializer(queryset, many=True)
#             return Response(serializer.data, status=200)
#         return Response({"error":"question id required"}, status=400)

#     def post(self, request):
#         question_id=request.GET.get('id', None)
#         try:
#             question=Question.objects.get(id=question_id)
#             question.is_enabled=True
#             question.save()

#             email = question.email
#             email=question.email
#             if not email:
#                 email = question.user.email
#         except Exception as e:
#             print(e)
#             return Response({"error":"Question not found"}, status=400)
#         serializer=AnswerCreateSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             serializer.validated_data['question']=question
#             serializer.save()
#             if not question.is_anonymous:
#                 email_sender(title="BAAANG!", body="Your question is answered", email=email)
#             # Return the serialized data with a 201 Created status code
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)

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

# Chat APP
class MyInbox(APIView):
    serializer_class = MessageSerializer
    def get(self, request):
        cookie=request.GET.get('cookie', None)
        if cookie:
            chat=Messages.objects.filter(room_id=cookie)
            serializer=MessageSerializer(chat,many=True)
            return Response({"data":serializer.data}, status=200)
        elif request.user.is_authenticated:
            chats=MessageRoom.objects.all()
            serializer=MessageRoomSerializer(chats,many=True)
            return Response({"data":serializer.data}, status=200)
        return Response({"error":"COOKIE is required"}, status=400)

    def post(self, request):
        serializer=MessageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        try:
            cookie=request.GET.get('cookie', None)
            instance = MessageRoom.objects.get(cookie=cookie)
            instance.delete()
            return Response({"succes":"Room succesfully deleted"},status=200)
        except:
            return Response({"error":"Room not found"}, status=400)

class MessageRoomCreate(APIView):
    def get(self,request):
        cookie=request.GET.get('cookie', None)
        try:
            if not request.user.is_authenticated:
                MessageRoom.objects.get_or_create(cookie=cookie)
                return Response({"message":"GOOD!"}, status=200)
            return Response({"message":"you can not create a chat!"}, status=200)
        except Exception as e:
            return Response({"error":str(e)}, status=400)

# MENTOR MATCH

class MentormatchScholierView(generics.CreateAPIView):
    serializer_class=MentorMatchScholierSerializer
    queryset=MentorMatchScholier.objects.all()
    permission_classes=[IsAuthenticated]
    def find_mentor(self, id):
        try:
            instance = MentorMatchScholier.objects.get(id=id)
        except Exception as e:
            print(e)
            return "Error"

        scholiers = MentorForScholier.objects.filter(study__name=instance.study.name,
                                                     university__name=instance.university.name)
                            
        for scholier in scholiers:
            # print(instance.is_replied)
            # print(instance.id)
            if not instance.is_replied:
                token = generate_token(user_id=id, student_id=scholier.id, user_type='scholier')

                # email_by_template(subject="Klik op de link om een mentor te worden voor een scholier",
                #                 ctx={'mentor_name':scholier.name,'mentor_unsubscribe':scholier.id, 'token':token}, #{str(one_time_link)+str(token)}
                #                 template_path=config('MENTOR_CLICK_TOKEN'), to=[scholier.email])
                

                email_by_template(subject="Klik op de link om een mentor te worden voor een scholier",
                ctx={'mentor_name':scholier.name,'mentor_unsubscribe':scholier.id, 'token':token,
                        'mentor_password':scholier.user.username, 'mentor_email':scholier.user.email}, #{str(one_time_link)+str(token)}
                template_path=config('MENTOR_CLICK_TOKEN-NEW'), to=[scholier.email])

                print(f"Email is sent for {scholier.email}")
                time.sleep(24*3600)
        instance = MentorMatchScholier.objects.get(id=id)
        if not instance.is_replied:
            email_sender_for_admin(title="Any mentor did not click or we don't have a mentor!", body=f"""
                        please add more mentors for scholier and the study is --> {instance.study}!,
                        University is --> {instance.university}!,
                    """, emails=["fayyoz1@mail.ru", "hiraanwar1998@gmail.com", "EvaSofia_@live.nl"])
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()
        email = instance.email if instance.email else instance.user.email

        email_by_template(subject="Beste Scholier!",
                ctx={'mentee_unsubscribe':instance.id},
                template_path='scholier_register.html', to=[email])

        id = instance.id
        find_mentor_thread = threading.Thread(target=self.find_mentor, args=(id,))
        find_mentor_thread.start()
        print("THREAD")


class JobTitleView(generics.ListAPIView):
    # queryset = JobTitle.objects.all()
    serializer_class = JobTitleSerializer
    permission_classes=[AllowAny]

    def get_queryset(self):
        pk = self.kwargs.get('pk')  # Retrieve 'pk' from the URL kwargs
        return JobTitle.objects.filter(sector=pk)

class SectorView(generics.ListAPIView):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [AllowAny]

class MentormatchStudentView(generics.CreateAPIView):
    serializer_class=MentorMatchStudentSerializer
    queryset=MentorMatchStudent.objects.all()
    permission_classes=[IsAuthenticated]

    def find_mentor(self, id):
        try:
            instance = MentorMatchStudent.objects.get(id=id)
        except Exception as e:
            print(e)
            return "Error"

        student_mentors = MentorForStudent.objects.filter(job_title = instance.job_title)

        for mentor in student_mentors:

            if not instance.is_replied:
                token = generate_token(user_id=id, student_id=mentor.id, user_type='student')

                email_by_template(subject="⁠Klik op de link om een mentor te worden voor een student",
                                ctx={'mentor_name':mentor.name,'mentor_unsubscribe':mentor.id, 'token':token}, #{str(one_time_link)+str(token)}
                                template_path='mentor_click_token.html', to=[mentor.email])

                print(f"Email is sent for {mentor.email}")
                time.sleep(24*3600)
        instance = MentorMatchStudent.objects.get(id=id)
        if not instance.is_replied:
            email_sender_for_admin(title="We don't have mentor for that Student!", body=f"""
                        please add more mentors for student and the job title is --> {instance.job_title}!,
                    """, emails=["fayyoz1@mail.ru", "hiraanwar1998@gmail.com", "EvaSofia_@live.nl"])

    def perform_create(self, serializer):
        print(self.request.user)
        instance = serializer.save()
        instance.user = self.request.user
        instance.save()

        email_sender(title="Beste Student!", body=f"""
                    Wat fantastisch dat je een
                    mentor-match-request hebt
                    ingediend! We hopen dat
                    het proces vlot is verlopen.

                    We zijn vol enthousiasme
                    bezig met het doorzoeken
                    """, email=instance.user.email)

        id = instance.id
        find_mentor_thread = threading.Thread(target=self.find_mentor, args=(id,))
        find_mentor_thread.start()
        print("THREAD")
from django.contrib.auth import authenticate

class MentorForScholierView(generics.CreateAPIView):
    serializer_class=MentorForScholierSerializer
    queryset=MentorForScholier.objects.all()

    def find_mentor(self, mentor_obj):
        # mentor_obj=MentorForScholier.objects.get(id)
        mentee_objects=MentorMatchScholier.objects.filter(study__name=mentor_obj.study.name, 
                                                          university__name=mentor_obj.university.name, 
                                                          is_replied=False)
        for obj in mentee_objects:
            token = generate_token(user_id=obj.id, student_id=mentor_obj.id, user_type='scholier')
            
            user = authenticate(username=mentor_obj.user.username, password=mentor_obj.user.username)
            mentor_email = " "
            mentor_password = " "
            print(f"{user} from authentication!")
            if user:
                mentor_email = mentor_obj.user.email
                mentor_password = mentor_obj.user.username             
            email_by_template(subject="Klik op de link om een mentor te worden voor een scholier",
                            ctx={'mentor_name':mentor_obj.name,'mentor_unsubscribe':mentor_obj.id, 'token':token,
                                'mentor_password':mentor_password, 'mentor_email':mentor_email}, #{str(one_time_link)+str(token)}
                            template_path=config('MENTOR_CLICK_TOKEN-NEW'), to=[mentor_obj.email])

            print(f"Email is sent for {mentor_obj.email}")
            time.sleep(24*3600)

    def perform_create(self, serializer):
        instance = serializer.save()
        email = instance.email
        name = instance.name
        print(instance)

        try:
            user = User.objects.get(email=email)
        except:
            username = username_generator(name=name)
            user = User.objects.create(username = username, email=email)
            user.set_password(username)
            user.save()
        instance.user = user
        instance.save()
        # mentor = MentorForScholier.objects.filter(id=instance.id)
        # mentor.user = user
        # print(mentor.user)
        # Then refresh to get the updated instance
        # instance.refresh_from_db()
        try:
            MentorForScholier.objects.get(email=instance.email)
            email_by_template(subject="⁠Bedankt dat jij een mentor bent voor een scholier!",
                    ctx={'name':instance.name, 'mentor_unsubscribe':instance.id},
                    template_path='mentor-register.html', to=[instance.email])
        except Exception as e:
            print(e)
            pass


        find_mentor_thread = threading.Thread(target=self.find_mentor, args=(instance,))
        find_mentor_thread.start()


class MentorForReRunView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        mentor_email=request.GET.get('mentor_email', None)

        mentor_objs = MentorForScholier.objects.filter(email=mentor_email)
        for mentor_obj in mentor_objs:
            if mentor_obj:
                try:
                    user = User.objects.get(email=mentor_obj.email)
                    mentor_obj.user = user
                    mentor_obj.save()
                except:
                    username = username_generator(name=mentor_obj.name)
                    user = User.objects.create(username = username, email=mentor_obj.email)
                    user.set_password(username)
                    user.save()
                    mentor_obj.user = user
                    mentor_obj.save()
                mentee_objects=MentorMatchScholier.objects.filter(study__name=mentor_obj.study.name, 
                                                            university__name=mentor_obj.university.name, 
                                                            is_replied=False)
                # serializer = MentorMatchScholierSerializer(mentee_objects, many=True)
                for obj in mentee_objects:
                    token = generate_token(user_id=obj.id, student_id=mentor_obj.id, user_type='scholier')

                    email_by_template(subject="Klik op de link om een mentor te worden voor een scholier",
                                    ctx={'mentor_name':mentor_obj.name,'mentor_unsubscribe':mentor_obj.id, 'token':token,
                                        'mentor_password':mentor_obj.user.username, 'mentor_email':mentor_obj.user.email}, #{str(one_time_link)+str(token)}
                                    template_path=config('MENTOR_CLICK_TOKEN-NEW'), to=[mentor_obj.email])

                    print(f"Email is sent for {mentor_obj.email}")
            # return Response({"emails are sent for:": serializer.data}, status=200)
        return Response({"detail":"mentor not found"}, status=200)


# 1. Klik op de link om een mentor te worden voor een scholier
# 2. ⁠Bedankt dat jij een mentor bent voor een scholier
# 3. ⁠YESS!! We hebben een mentor gevonden
# 4. ⁠Klik op de link om een mentor te worden voor een student

# subject="Plese click on the link to be a mentor for scholier"
# subject="thank you for your being a  Scholier mentor!",
# subject="Feedback!",
# subject="BAAANG we found a mentor for you!",
# subject="Plese click on the link to be a mentor for student"

class MentorForStudentView(generics.CreateAPIView):
    serializer_class=MentorForStudentSerializer
    queryset=MentorForStudent.objects.all()

    def find_mentor(self, mentor_obj):
        # mentor_obj=MentorForScholier.objects.get(id)
        mentee_objects=MentorMatchStudent.objects.filter(job_title=mentor_obj.job_title, is_replied=False)

        for obj in mentee_objects:
            token = generate_token(user_id=obj.id, student_id=mentor_obj.id, user_type='student')

            email_by_template(subject="⁠Klik op de link om een mentor te worden voor een student",
                            ctx={'mentor_name':mentor_obj.name,'mentor_unsubscribe':mentor_obj.id, 'token':token}, #{str(one_time_link)+str(token)}
                            template_path='mentor_click_token.html', to=[mentor_obj.email])

            print(f"Email is sent for {mentor_obj.email}")
            time.sleep(24*3600)

    def perform_create(self, serializer):
        instance = serializer.save()
        email = instance.email
        name = instance.name
        try:
            user = User.objects.get(email=email)
        except:
            username = username_generator(name=name)
            user = User.objects.create(username = username, email=email)
            user.set_password(username)
            user.save()
        instance.user = user
        try:
            MentorForStudent.objects.get(email=instance.email)
            email_by_template(subject="thank you for your being a  Student mentor!",
                    ctx={'name':instance.name, 'mentor_unsubscribe':instance.id},
                    template_path='mentor-register.html', to=[instance.email])
        except Exception as e:
            print(e)
            pass


        find_mentor_thread = threading.Thread(target=self.find_mentor, args=(instance,))
        find_mentor_thread.start()



href="https://temma-demo.vercel.app/login-chat?token="


from chatting.models import Message
class OneTimeLinkForMentorView(APIView):
    # permission_classes=[IsAuthenticated]
    def ask_feedback(self, mentor_email, std_email, mentor_name, mentor_instance_id, user_instance_id):
        time.sleep(7*24*3600)
        print('I am sending feedback emails')
        email_by_template(subject="Feedback!",
                ctx={'mentor_name':mentor_name,
                    'mentor_unsubscribe':mentor_instance_id},
                template_path='feedback_mentor.html', to=[mentor_email])

        email_by_template(subject="Feedback!",
                ctx={'mentor_name':mentor_name,
                    'mentee_unsubscribe':user_instance_id},
                template_path='feedback_mentee.html', to=[std_email])

    def get(self,request):
        token = request.GET.get('token', None)
        # print(token)
        try:
            payload = decode_token(token)
            user_id = payload['user_id']
            user_type=payload['user_type']
            student_id = payload['student_id']
            study = ""
            if user_type == 'student':
                # print(f"User ID {user_id}")
                user_instance=MentorMatchStudent.objects.get(id=user_id)
                # print(f"instance Scholier {user_instance.is_replied}")
                # print(f"Scholier ID {student_id}")
                mentor_instance=MentorForStudent.objects.get(id=student_id)
                study = mentor_instance.job_title
                room_name = f"{mentor_instance.name}+{str(user_instance.user.email)}"
                try:
                    room = Room.objects.get(room_name=room_name, job_title=user_instance.job_title)
                except:
                    room = Room.objects.create(room_name=room_name, job_title=user_instance.job_title)
                    content = "Hey! Ik ben je mentor-match! Hoe kan ik je helpen :)"
                    Message.objects.create(user=mentor_instance.user, room=room, content=content)
            else:
                user_instance=MentorMatchScholier.objects.get(id=user_id)
                mentor_instance=MentorForScholier.objects.get(id=student_id)
                study=mentor_instance.study
                room_name = f"{mentor_instance.name}+{str(user_instance.user.email)}"
                try:
                    room = Room.objects.get(room_name=room_name, study_name=user_instance.study)
                except:
                    room = Room.objects.create(room_name=room_name, study_name=user_instance.study)
                    content = "Hey! Ik ben je mentor-match! Hoe kan ik je helpen :)"
                    Message.objects.create(user=mentor_instance.user, room=room, content=content)
                # print(f"instance Scholier {user_instance.is_replied}")
                # print(f"Scholier ID {student_id}")

            user_instance.is_replied=True
            user_instance.save()

            try:
                mentor = User.objects.get(email=mentor_instance.email)
            except:
                username = username_generator(name=mentor_instance.name)
                mentor = User.objects.create(username = username, email=mentor_instance.email)
                mentor.set_password(username)
                mentor.save()

            mentor_instance.user = mentor
            mentor_instance.save()


            room.users.set([user_instance.user.id, mentor.id])

            email_by_template(subject="⁠YESS!! We hebben een mentor gevonden",
                            ctx={'mentor_name':mentor_instance.name, 'mentor_email':mentor.email, "mentee_name":user_instance.user.username,
                                'mentee_unsubscribe':user_instance.id, 'room_id':room.id},
                            template_path=config('MENTOR_DATA_FOR_MENTEE'), to=[user_instance.email])

            # email for mentor
            # email_by_template(subject="",
            #                 ctx={'mentor_name':mentor_instance.name, 'email_scholier':user_instance.user.email,
            #                      'mentee_name':user_instance.user.username, "mentor_email": mentor_instance.email,
            #                      "mentor_password":mentor.username,
            #                      'mentor_unsubscribe':mentor_instance.id, "room_id":room.id},

            #                 template_path=config('MENTEE_DATA_FOR_MENTOR'), to=[mentor_instance.email])

            find_mentor_thread = threading.Thread(target=self.ask_feedback, args=(mentor_instance.email, user_instance.user.email, mentor_instance.name, mentor_instance.id, user_instance.id))
            find_mentor_thread.start()

            data = {"room_id":room.id, 'mentor_name':mentor_instance.name, 
                    "mentor_password":mentor.username,'mentor_email':mentor.email}

            return Response({'data':data}, status=200)
        except jwt.ExpiredSignatureError:
            return Response({"detail":"Your token is expired!"}, status=400)
        except jwt.DecodeError:
            return Response({"detail":"Something went wrong, please contact admins!"}, status=404)

    # permission_classes = [IsAdminUser]

class MentorTest(APIView):

    def get(self, request):
        # University.objects.all().delete()
        with open("./studies_studiekuze_last.json", "r") as file:
            data = json.load(file)
        # Study.objects.all().delete()
        for d in data:
            degree=None
            if 'bachelor' in d['degree']:
                degree = 'B'
            elif 'master' in d['degree']:
                degree = 'M'
            if degree:
                print(degree)
                print(d['university'])
                univ = University.objects.get(degree=degree, name=d['university'])
                filt = Study.objects.filter(university=univ, name = d['study'], degree=degree)
                if not filt:
                    Study.objects.create(university=univ, name = d['study'], degree=degree)

            # degree=None
            # if 'bachelor' in d['degree']:
            #     degree = 'B'
            # elif 'master' in d['degree']:
            #     degree = 'M'
            # f = University.objects.filter(degree=degree, name=d['university'])
            # if not f:
            #     if degree:
            #         print("none")
            #         # univ = University.objects.get(degree=degree, name=d['university'])
            #         University.objects.create(degree=degree, name=d['university'], logo=d['logo'])


        # seen = defaultdict(list)
        # duplicates = []
        # for obj in Study.objects.all():
        #     identifier = (obj.name, obj.degree, obj.university)

        #     if identifier in seen:
        #         duplicates.append(obj.pk)
        #     else:
        #         seen[identifier].append(obj.pk)

        # # Delete duplicates in batches
        # batch_size=999
        # for i in range(0, len(duplicates), batch_size):
        #     with transaction.atomic():
        #         Study.objects.filter(pk__in=duplicates[i:i+batch_size]).delete()
        # for key, value in univ_bach.items():
        #     univ = University.objects.create(degree='B', name = key, logo=logos[key])
        #     for st in value:
        #         Study.objects.create(degree='B',university=univ, name=st)
    #     class StudentAdd(APIView):
    # def get(self, request):
# Ouidad Batou Ouidad Batou
        # email_by_template(subject="BAAANG we found a mentor for you!",
        #                 ctx={'mentor_name':"fayyoz", 'mentor_email':"fayyoz1@mail.ru", "mentor_study":"study",
        #                     'mentee_unsubscribe':2},
        #                 template_path='mentor-details-for-student.html', to=['fayyoz1@mail.ru'])

        # email_by_template(subject="",
                        # ctx={'mentor_name':mentor_instance.name, 'email_scholier':user_instance.email,
                        #         'mentor_unsubscribe':mentor_instance.id},
                        # template_path='mentee_data_for_mentor.html', to=[mentor_instance.email])

        return Response({"detail":"please provide me with id"}, status=200)
        # path = "./question/Mentoren voor Mentor Match  (2).xlsx"
        # if not DEBUG:
        #     path = "/home/Thiernobalde95/temma_pytanywhere/temma/question/Mentoren voor Mentor Match  (2).xlsx"
        # df = pd.read_excel(path)
        # for i in range(17, 80):
        #     try:
        #         name = df['Name'][i]
        #         email = df['email'][i]
        #         linkedin = df['linkedin'][i]
        #         MentorForScholier.objects.create(name=name, email=email, linkedin_link=linkedin)
        #         email_by_template(subject="thank you for your being a mentor!", ctx={'name':name},
        #                             template_path='mentor-register.html', to=[email]
        #                             )
        #         print(f"{i}  f done!")
        #     except:
        #         continue

class UnsubscribeView(APIView):
    def get(self, request):
        mentor_id = request.GET.get('mentor_unsubscribe', None)
        mentee_id = request.GET.get('mentee_unsubscribe', None)
        print(f"MENTEE {mentee_id}")
        print(f"MENTor {mentor_id}")
        if mentee_id:
            try:
                MentorMatchScholier.objects.get(id=mentee_id).delete()
                return Response({"detail":"you are unsubscribed succesfully"}, status=200)
            except Exception as e:
                return Response({"detail":"id not found"}, status=404)
        elif mentor_id:
            try:
                MentorForScholier.objects.get(id=mentor_id).delete()
                return Response({"detail":"you are unsubscribed succesfully"}, status=200)
            except Exception as e:
                return Response({"detail":"id not found"}, status=404)

        return Response({"detail":"please provide me with id"}, status=404)



class UniversityView(APIView):
    def get(self, request):
        degree = request.GET.get('degree', None)
        if not degree:
            return Response({"detail":'degree is required'}, status=400)
        queryset = University.objects.filter(degree=degree)

        serializer = UniversitySerializer(queryset, many=True)

        return Response({"data":serializer.data}, status=200)

class StudyView(APIView):
    def get(self, request):
        id = request.GET.get('university', None)
        if not id:
            return Response({"detail":'university is required'}, status=400)
        university=University.objects.get(id=id)
        queryset = Study.objects.filter(university=university)
        serializer = StudySerializer(queryset, many=True)

        return Response({"data":serializer.data}, status=200)

class StudiesListView(APIView):
    def get(self, request):
        degree = request.GET.get('degree', None)

        data = Study.objects.filter(degree=degree)
        serializer = StudySerializer(data, many=True)
        return Response({"data":serializer.data}, status=200)

class UniversitiesListView(APIView):
    def get(self, request):
        study = request.GET.get('study', None)
        degree = request.GET.get('degree', None)

        data = Study.objects.filter(name=study, degree=degree)
        serializer = StudySerializer(data, many=True)
        return Response({"data":serializer.data}, status=200)

class PopularStudiesView(APIView):
    def get(self, request):
        degree = request.GET.get('degree')
        list_degrees = ["M", "B"]
        if degree in list_degrees:
            if degree == 'B':
                path = './question/data_bachelors.json'
                if not DEBUG:
                    path= config('BACHELORS_DATA') #'/home/demotemma1/temma_pytanywhere/temma/question/data_bachelors.json'
                with open(path, 'r') as file:
                    data = json.load(file)
            else:
                path = './question/data_masters.json'
                if not DEBUG:
                    path= config('MASTERS_DATA') #'/home/demotemma1/temma_pytanywhere/temma/question/data_masters.json'
                with open(path, 'r') as file:
                    data = json.load(file)

            random_10_objects = random.sample(list(data), 5) if len(data) >= 5 else data
            return Response({"data":random_10_objects}, status=200)

        return Response({"detail":"degree is required!"}, status=400)

class AllStudiesWithInformationView(APIView):
    def get(self, request):
        degree = request.GET.get('degree')
        list_degrees = ["M", "B"]
        if degree in list_degrees:
            if degree == 'B':
                path = './question/data_bachelors.json'
                if not DEBUG:
                    path=config('BACHELORS_DATA') #'/home/demotemma1/temma_pytanywhere/temma/question/data_bachelors.json'
                with open(path, 'r') as file:
                    data = json.load(file)
            else:
                path = './question/data_masters.json'
                if not DEBUG:
                    path=config('MASTERS_DATA') #'/home/demotemma1/temma_pytanywhere/temma/question/data_masters.json'
                with open(path, 'r') as file:
                    data = json.load(file)
            return Response({"data":data}, status=200)
# click on the link

class SendEmailNewMentor(APIView):
    def get(self, request):
        students=MentorMatchScholier.objects.filter(is_replied=False)
        for student in students:
            mentor = MentorForScholier.objects.filter(study=student.study, university=student.university).first()
            if not mentor:
                email_sender(title="Any mentor did not click or we don't have a mentor!", body=f"""
                        please add more mentors for scholier and the study is --> {student.study}!,
                        University is --> {student.university}!,
                    """, email="fayyoz1@mail.ru")
                continue

            token = generate_token(user_id=student.id, student_id=mentor.id, user_type='scholier')

            email_by_template(subject="Klik op de link om een mentor te worden voor een scholier",
                                ctx={'mentor_name':mentor.name,'mentor_unsubscribe':mentor.id, 'token':token}, #{str(one_time_link)+str(token)}
                                template_path=config('MENTOR_CLICK_TOKEN'), to=[mentor.email])

        return Response({"detail":"Emails are sent, please visit after a week!"}, status=200)
