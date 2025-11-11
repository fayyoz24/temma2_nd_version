
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import (Exists, OuterRef, 
                                Case, When, 
                                BooleanField, 
                                Count, Q, F)
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .serializers import (NewsArticleCreateUpdateSerializer, 
                            AuthorSerializer,
                            LanguageSerializer,
                            NewsArticleDetailByLanguageSerializer
                            )
from .models import (NewsArticle, 
                    UserNewsView, 
                    Author, 
                    Language)
from rest_framework.views import APIView
from rest_framework import generics
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView
    
class NewsArticleByAuthorView(APIView):
    def get(self, request, pk):
        author = Author.objects.get(id=pk)
        author_data = AuthorSerializer(author).data
        queryset = NewsArticle.objects.filter(author = pk)
        serializer = NewsArticleDetailByLanguageSerializer(queryset, many=True, context={'request': request})

        return Response({"author":author_data, "data": serializer.data}, status=200)

class NewsArticleCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = NewsArticleCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return NewsArticle.objects.all().order_by("-id")


class LanguageListView(ListAPIView):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class FilterDataBasedOnLevelView(APIView):
    pass

class NewsArticleListView(APIView):
    """
    Provides a list of articles separated into seen and unseen for regular users,
    with unseen articles count for each author.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # Annotate is_seen for articles based on UserNewsView
        queryset = NewsArticle.objects.annotate(
            is_seen=Exists(
                UserNewsView.objects.filter(
                    user=user,
                    article=OuterRef('pk')
                )
            )
        ).filter(
            scheduled_for__lte=timezone.now()  # Published articles
        )

        # Get all authors and their unseen article counts
        authors_with_unseen = (
            Author.objects.annotate(
                unseen_article_num=Count(
                    'newsarticle',
                    filter=Q(
                        newsarticle__scheduled_for__lte=timezone.now(),  # Published articles
                    ) & ~Exists(
                        UserNewsView.objects.filter(
                            user=user,
                            article=OuterRef('newsarticle__id')
                        )
                    )
                )
            ).values('id', 'name', 'prof_pic', 'unseen_article_num')
        )

        # Get unseen articles count
        unseen_articles = queryset.filter(
            ~Exists(
                UserNewsView.objects.filter(
                    user=user,
                    article=OuterRef('pk')
                )
            )
        )

        # Transform authors data
        authors_data = [
            {
                'author_id': author['id'],
                'name': author['name'],
                'prof_pic': author['prof_pic'],
                'unseen_article_num': author['unseen_article_num']
            } 
            for author in authors_with_unseen
        ]

        custom_order = {
            'DUO': 1,
            'Dienst Toeslagen': 7,
            'Belastingdienst': 6,
            'Nibud': 3,
            # 'Landelijk Centrum Studiekeuze': 7,
            'Studielink': 5,
            'Mln OCW': 4,
            "ECIO": 2
        }
        
        # Sort authors based on the custom order
        authors_data.sort(key=lambda x: custom_order.get(x['name'], 999))

        return Response({
            "all_unseen_num": unseen_articles.count(),
            "authors": authors_data
        })

class NewsArticleDetailView(RetrieveAPIView):
    serializer_class = NewsArticleDetailByLanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = NewsArticle.objects.select_related(
            'author', 'original_language'
        ).prefetch_related('versions__language')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(scheduled_for__lte=timezone.now())
            
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
            
        # Only mark as seen if the article is published
        if instance.scheduled_for <= timezone.now():
            UserNewsView.objects.get_or_create(
                user=request.user,
                article=instance
            )
            
        # Pass request in the context explicitly
        serializer = self.get_serializer(instance, context={'request': request})
        return Response(serializer.data)



class ToggleUserNewsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, article_id):
        
        user = request.user
        article = get_object_or_404(NewsArticle, id=article_id)

        obj = UserNewsView.objects.filter(user=user, article=article).first()

        if obj:
            obj.delete()
            return Response({"detail": "View removed."}, status=status.HTTP_200_OK)
        else:
            UserNewsView.objects.create(user=user, article=article)
            return Response({"detail": "View added."}, status=status.HTTP_201_CREATED)
