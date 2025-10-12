from django.shortcuts import render
from .models import CoustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework import generics, response, status, permissions
from rest_framework.authentication import TokenAuthentication
# Create your views here.
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        user = CoustomUser.objects.get(id=res.data['id'])
        token = user.auth_token.key
        return response.Response(
            {'user': UserSerializer(user, context={'request': request}).data, 'token': token},
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return response.Response(ser.validated_data, status=status.HTTP_200_OK)

class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return response.Response(UserSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        ser = UserSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return response.Response(ser.data)