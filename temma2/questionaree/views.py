from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
import json
from rest_framework.response import Response
from temma2.settings import DEBUG
from decouple import config

path = config('QUESTIONS_JSON_PATH', default='./questionaree/questions.json')

class AllQuestionsView(APIView):
    def get(self, request, *args, **kwargs):
        with open(path) as f:
            questions = json.load(f)
        return Response(questions, status=200)