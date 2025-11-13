from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (RegisterUserView, 
                CustomTokenObtainPairView, 
                RegionListView, 
                DeleteAccountView,
                ChangePasswordView,
                RequestPasswordResetEmailView,
                SetNewPasswordAPIView
                )


urlpatterns = [
    path("signup/", RegisterUserView.as_view(), name="register"),
    path("region-list/", RegionListView.as_view(), name="region-list/"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("request-reset-email/", RequestPasswordResetEmailView.as_view(), name="request-reset-email"),
    path("set-new-password/", SetNewPasswordAPIView.as_view(), name="set-new-password"),
]
