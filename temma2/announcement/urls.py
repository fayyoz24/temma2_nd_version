from django.urls import path, include
# from .views import (NewsArticleCreateUpdateView, NewsArticleListView, 
#                     NewsArticleCreateView,NewsArticleByAuthorView, AllAuthorsView,
#                     NewsArticleDetailView, LanguageListView)

from .views import (
    NewsArticleListView, NewsArticleCreateView,
    LanguageListView, NewsArticleByAuthorView, 
    NewsArticleDetailView, ToggleUserNewsView
)


urlpatterns = [
    path('', NewsArticleListView.as_view(), name='news-list'),
    path('create', NewsArticleCreateView.as_view(), name='news-create'),
    path('<int:pk>/', NewsArticleDetailView.as_view(), name='articles-of-author'),
    path('language-list', LanguageListView.as_view(), name='language-list'),
    
    path("articles/<int:article_id>/toggle-view/", ToggleUserNewsView.as_view(), name="toggle-user-news-view"),
    # path('all-authors', AllAuthorsView.as_view(), name='all-authors'),
    # path('<int:pk>/', NewsArticleCreateUpdateView.as_view(), name='news-detail'),
    path('articles-of-author/<int:pk>/', NewsArticleByAuthorView.as_view(), name='articles-of-author'),
]