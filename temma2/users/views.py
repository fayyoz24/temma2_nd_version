
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .serializers import (UserSerializer, 
                            CustomTokenObtainPairSerializer,
                            ChangePasswordSerializer,
                            ResetPasswordEmailRequestSerializer,
                            SetNewPasswordSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import GenericAPIView, UpdateAPIView
from django.utils.encoding import force_str, smart_bytes
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import twilio_whatsapp, email_by_template
from .models import CustomUser as User
from rest_framework.permissions import IsAuthenticated
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from decouple import config


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data.get("phone_number")
            try:
                # Send WhatsApp message using Twilio
                twilio_whatsapp(phone_number)
            except Exception as e:
                return Response(
                    {"detail": f"Failed to send WhatsApp message, please check your number!"},
                    status=400,
                )
            user = serializer.save()

            # generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            return Response(
                { 
                    "detail": "User registered successfully",
                    "tokens": tokens,
                    "user": {
                        "id": user.id,
                        "full_name": user.full_name,
                        "phone_number": user.phone_number,
                        "email": user.email,
                        "role": user.role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegionListView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from .serializers import RegionSerializer
        from .models import Region

        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)

class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user

        # prevent deleting superuser accounts
        if user.is_superuser:
            return Response(
                {"detail": "Superuser accounts cannot be deleted."},
                status=403,
            )

        user.delete()
        return Response(
            {"detail": "Your account has been deleted successfully."},
            status=204
        )

class ChangePasswordView(UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"detail": "old password is wrong!"}, status=400)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'detail': 'Password updated successfully!',
            }

            return Response(response, status=200)

        return Response(serializer.errors, status=400)

class RequestPasswordResetEmailView(GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                # ?token=cgshfm-8090070509dd553ceef551623db47e7e&uidb64=MTA/
                # absurl = config("ALLOWED_HOST")+f"/api/users/password-reset-confirm?token={token}&uidb64={uidb64}"
                absurl = config("FRONTEND_URL")+f"password-recover?token={token}&uidb64={uidb64}"
                email_by_template(subject="",
                            ctx={'username':user.full_name, 'absurl':absurl
                                 },

                            template_path='forgot-password.html', to=[email])
                # email_body = f'''
                # Hello {user.username}, \n Use link below to reset your passworddddddddddddd  n\'
                # {absurl}'''
           
                # email_sender(email=email, title='Reset your passsword', body=email_body)
                return Response({'detail': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
            return Response({"detail":"email is wrong!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetNewPasswordAPIView(GenericAPIView):

    def post(self, request):
        serializer=SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            password=serializer.validated_data['password']

            token = request.GET.get("token")
            uidb64=request.GET.get("uidb64")

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'detail': 'Token is not valid, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(password)
            user.save()

            return Response({'detail': 'Password reset successfully!'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
