from django.urls import path
from .views import AdvokateRequestListCreateView, AdvokateRequestDetailView

urlpatterns = [
    path("requests/", AdvokateRequestListCreateView.as_view(), name="advokate-request-list-create"),
    path("requests/<int:pk>/", AdvokateRequestDetailView.as_view(), name="advokate-request-detail"),
]
