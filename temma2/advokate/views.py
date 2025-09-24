from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import AdvokateRequest
from .serializers import AdvokateRequestSerializer


class AdvokateRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        requests = AdvokateRequest.objects.filter(user=request.user)
        serializer = AdvokateRequestSerializer(requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdvokateRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # assign logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdvokateRequestDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return AdvokateRequest.objects.get(pk=pk, user=user)

    def get(self, request, pk):
        req = self.get_object(pk, request.user)
        serializer = AdvokateRequestSerializer(req)
        return Response(serializer.data)

    def delete(self, request, pk):
        req = self.get_object(pk, request.user)
        req.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
