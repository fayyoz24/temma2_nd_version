
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Exists, OuterRef, Case, When, BooleanField
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .serializers import NewsArticleCreateUpdateSerializer, AuthorSerializer
from .models import NewsArticle, UserNewsView, Author
from rest_framework.views import APIView
from rest_framework import generics
from django.db.models import Count
from django.db.models.functions import Coalesce
from django.db.models import Count, Q, F

# class NewsArticleCreateView(generics.ListCreateAPIView):
#     """
#     This view allows admin and article authors to create articles.
#     """
#     permission_classes = [IsAdminUser]
#     serializer_class = NewsArticleCreateUpdateSerializer

#     def get_serializer_class(self):
#         if self.request.method in ['POST', 'PUT', 'PATCH']:
#             return NewsArticleCreateUpdateSerializer
#         return NewsArticleDetailSerializer
    
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user) 

#     def get_queryset(self):

#         queryset = NewsArticle.objects.all().order_by("-id")

#         return queryset

# # class NewsArticleListView(APIView):
# #     """
# #     Provides a list of articles separated into seen and unseen for regular users,
# #     with unseen articles further grouped by author.
# #     """
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         user = request.user

# #         # Annotate is_seen for articles based on UserNewsView
# #         queryset = NewsArticle.objects.annotate(
# #             is_seen=Exists(
# #                 UserNewsView.objects.filter(
# #                     user=user,
# #                     article=OuterRef('pk')
# #                 )
# #             ),
# #             is_published=Case(
# #                 When(scheduled_for__lte=timezone.now(), then=True),
# #                 default=False,
# #                 output_field=BooleanField(),
# #             )
# #         ).filter(is_published=True)

# #         # Separate seen and unseen articles
# #         seen_articles = queryset.filter(is_seen=True)
# #         unseen_articles = queryset.filter(is_seen=False)

# #         # Group unseen articles by author with count
# #         unseen_by_author = (
# #             unseen_articles
# #             .values('author__id', 'author__username')
# #             .annotate(
# #                 unseen_count=Count('id')
# #             )
# #             .order_by('-unseen_count')
# #         )

# #         # Serialize seen and unseen articles
# #         seen_serializer = NewsArticleDetailSerializer(seen_articles, many=True)
# #         unseen_serializer = NewsArticleDetailSerializer(unseen_articles, many=True)

# #         # Transform unseen by author to match the requested format
# #         unseen_author_data = [
# #             {
# #                 'author_id': item['author__id'], 
# #                 'unseen_article_num': item['unseen_count']
# #             } 
# #             for item in unseen_by_author
# #         ]

# #         return Response({
# #             "seen_articles": seen_serializer.data,
# #             "unseen_articles": unseen_serializer.data,
# #             "unseen_articles_by_author": unseen_author_data
# #         })

# class NewsArticleListView(APIView):
#     """
#     Provides a list of articles separated into seen and unseen for regular users,
#     with unseen articles count for each author.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         user = request.user

#         # Annotate is_seen for articles based on UserNewsView
#         queryset = NewsArticle.objects.annotate(
#             is_seen=Exists(
#                 UserNewsView.objects.filter(
#                     user=user,
#                     article=OuterRef('pk')
#                 )
#             )
#         ).filter(
#             scheduled_for__lte=timezone.now()  # Published articles
#         )

#         # Get all authors and their unseen article counts
#         authors_with_unseen = (
#             Author.objects.annotate(
#                 unseen_article_num=Count('newsarticle', filter=Q(
#                     newsarticle__scheduled_for__lte=timezone.now(),
#                     newsarticle__usernewsview__isnull=True
#                 ))
#             ).values('id', 'name', 'prof_pic', 'unseen_article_num')
#         )

#         # Separate seen and unseen articles
#         # seen_articles = queryset.filter(is_seen=True)
#         unseen_articles = queryset.filter(is_seen=False)

#         # Serialize seen and unseen articles
#         # seen_serializer = NewsArticleDetailSerializer(seen_articles, many=True)
#         # unseen_serializer = NewsArticleDetailSerializer(unseen_articles, many=True)

#         # Transform authors data
#         authors_data = [
#             {
#                 'author_id': author['id'],
#                 'name': author['name'],
#                 'prof_pic': author['prof_pic'],
#                 'unseen_article_num': author['unseen_article_num']
#             } 
#             for author in authors_with_unseen
#         ]

#         return Response({
#             "all_unseen_num":unseen_articles.count(),
#             # "seen_articles": seen_serializer.data,
#             # "unseen_articles": unseen_serializer.data,
#             "authors": authors_data
#         })

# class NewsArticleCreateUpdateView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     This view allows admin and article authors to retrieve, update, or delete articles.
#     """
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         queryset = NewsArticle.objects.annotate(
#             is_seen=Exists(
#                 UserNewsView.objects.filter(
#                     user=user,
#                     article=OuterRef('pk')
#                 )
#             ),
#             is_published=Case(
#                 When(scheduled_for__lte=timezone.now(), then=True),
#                 default=False,
#                 output_field=BooleanField(),
#             )
#         )
#         return queryset

#     def get_serializer_class(self):
#         if self.request.method in ['POST', 'PUT', 'PATCH']:
#             return NewsArticleCreateUpdateSerializer
#         return NewsArticleDetailSerializer

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def perform_update(self, serializer):
#         article = self.get_object()
#         # if self.request.user != article.author and not self.request.user.is_staff:
#         if not self.request.user.is_staff:
#             raise PermissionDenied("You don't have permission to edit this article.")
#         serializer.save()

#     def perform_destroy(self, instance):
#         # if self.request.user != instance.author and not self.request.user.is_staff:
#         if not self.request.user.is_staff:
#             raise PermissionDenied("You don't have permission to delete this article.")
#         instance.delete()

#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()

#         # Only allow viewing if published or if user is author/staff
#         # if not instance.is_published and not (request.user == instance.author or request.user.is_staff):
#         if not instance.is_published and not request.user.is_staff:
#             raise PermissionDenied("This article is not yet published")

#         # Mark as seen by saving to UserNewsView if the article is published
#         if instance.is_published:
#             UserNewsView.objects.get_or_create(
#                 user=request.user,
#                 article=instance
#             )

#         serializer = self.get_serializer(instance)
#         return Response(serializer.data)


    
# class AllAuthorsView(generics.ListAPIView):
#     serializer_class = AuthorSerializer
#     queryset = Author.objects.all()
#     permission_classes=[IsAdminUser]


# class TranslateGPTView(APIView):
#     permission_classes=[IsAuthenticated]

#     def get(self, request, article_id):
#         pass

# from .models import Language
# from .serializers import NewsArticleDetailByLanguageSerializer, LanguageSerializer
# from rest_framework.generics import ListAPIView, RetrieveAPIView

# class NewsArticleDetailView(RetrieveAPIView):
#     queryset = NewsArticle.objects.filter(
#         scheduled_for__lte=timezone.now()
#     ).select_related(
#         'author', 'original_language'
#     ).prefetch_related('versions__language')
    
#     serializer_class = NewsArticleDetailByLanguageSerializer

# class LanguageListView(ListAPIView):
#     queryset = Language.objects.all()
#     serializer_class = LanguageSerializer











from .serializers import NewsArticleCreateUpdateSerializer, NewsArticleDetailByLanguageSerializer
from .models import Language
from .serializers import LanguageSerializer
from rest_framework.generics import ListAPIView, RetrieveAPIView


# class NewsArticleListView(APIView):
#     """
#     Provides a list of articles separated into seen and unseen for regular users,
#     with unseen articles count for each author.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         user = request.user

#         # Annotate is_seen for articles based on UserNewsView
#         queryset = NewsArticle.objects.annotate(
#             is_seen=Exists(
#                 UserNewsView.objects.filter(
#                     user=user,
#                     article=OuterRef('pk')
#                 )
#             )
#         ).filter(
#             scheduled_for__lte=timezone.now()  # Published articles
#         )

#         # Get all authors and their unseen article counts
#         authors_with_unseen = (
#             Author.objects.annotate(
#                 unseen_article_num=Count('newsarticle', filter=Q(
#                     newsarticle__scheduled_for__lte=timezone.now(),
#                     newsarticle__usernewsview__isnull=True
#                 ))
#             ).values('id', 'name', 'prof_pic', 'unseen_article_num')
#         )

#         # Separate seen and unseen articles
#         # seen_articles = queryset.filter(is_seen=True)
#         unseen_articles = queryset.filter(is_seen=False)

#         # Transform authors data
#         authors_data = [
#             {
#                 'author_id': author['id'],
#                 'name': author['name'],
#                 'prof_pic': author['prof_pic'],
#                 'unseen_article_num': author['unseen_article_num']
#             } 
#             for author in authors_with_unseen
#         ]

#         return Response({
#             "all_unseen_num":unseen_articles.count(),
#             # "seen_articles": seen_serializer.data,
#             # "unseen_articles": unseen_serializer.data,
#             "authors": authors_data
#         })
    
from .serializers import NewsArticleDetailByLanguageSerializer
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
            'Dienst Toeslagen': 6,
            'Belastingdienst': 5,
            'Nibud': 2,
            # 'Landelijk Centrum Studiekeuze': 7,
            'Studielink': 4,
            'Mln OCW': 3,
            "ECIO - Expertisecentrum Inclusief Onderwijs": 7
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
    def post(self, request, article_id):
        user = request.user
        article = get_object_or_404(NewsArticle, id=article_id)

        obj = UserNewsView.objects.filter(user=user, article=article).first()

        if obj:
            obj.delete()
            return Response({"detail": "View removed."}, status=status.HTTP_200_OK)
        else:
            UserNewsView.objects.create(user=user, article=article)
            return Response({"detail": "View added."}, status=status.HTTP_201_CREATED)
