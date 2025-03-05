from rest_framework import generics, permissions
from user_app.serializers import UserSerializer
from user_app.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
