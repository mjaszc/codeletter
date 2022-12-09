from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class HelloView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        content = {"message": "Hello this is my first request"}
        return Response(content)
