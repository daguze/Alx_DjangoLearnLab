from django.shortcuts import render, get_object_or_404
from rest_framework import generics, response, status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserSerializer
from posts.models import User 



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        user = CustomUser.objects.get(id=res.data['id'])
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


# accounts/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import CustomUser

class FollowUserView(generics.GenericAPIView):
    """
    API view to allow a user to follow another user.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all() # Defines the set of objects this view can act on.

    def post(self, request, *args, **kwargs):
        user_to_follow = self.get_object() # Retrieves user based on 'pk' from URL.
        user = request.user

        if user == user_to_follow:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.following.filter(pk=user_to_follow.pk).exists():
            return Response(
                {"error": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.following.add(user_to_follow)
        
        # Returns a success message.
        return Response(
            {"detail": f"Successfully followed {user_to_follow.username}."},
            status=status.HTTP_200_OK
        )


class UnfollowUserView(generics.GenericAPIView):
    """
    API view to allow a user to unfollow another user.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        user_to_unfollow = self.get_object()
        user = request.user

        if not user.following.filter(pk=user_to_unfollow.pk).exists():
            return Response(
                {"error": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user.following.remove(user_to_unfollow)
        
        return Response(
            {"detail": f"Successfully unfollowed {user_to_unfollow.username}."},
            status=status.HTTP_200_OK
        )


class UserListView(generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        users = self.get_queryset()
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


