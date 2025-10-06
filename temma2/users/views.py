
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework_simplejwt.tokens import RefreshToken
from .utils import twilio_whatsapp

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
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from .serializers import RegionSerializer
        from .models import Region

        regions = Region.objects.all()
        serializer = RegionSerializer(regions, many=True)
        return Response(serializer.data)

