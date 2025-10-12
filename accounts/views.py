# accounts/views.py

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    """
    API view for user registration. Returns user data and auth token.
    """
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        user = CustomUser.objects.get(id=res.data['id'])
        token = user.auth_token.key
        return Response(
            {'user': UserSerializer(user, context={'request': request}).data, 'token': token},
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    """
    API view for user login. Returns user data and auth token.
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class ProfileView(APIView):
    """
    API view for retrieving and updating the authenticated user's profile.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class FollowUserView(generics.GenericAPIView):
    """
    API view to allow a user to follow another user.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        user_to_follow = self.get_object()
        user = request.user

        if user == user_to_follow:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        if user.following.filter(pk=user_to_follow.pk).exists():
            return Response({"error": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)

        user.following.add(user_to_follow)
        return Response({"detail": f"Successfully followed {user_to_follow.username}."}, status=status.HTTP_200_OK)

class UnfollowUserView(generics.GenericAPIView):
    """
    API view to allow a user to unfollow another user.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = CustomUser.objects.all()

    def post(self, request, *args, **kwargs):
        user_to_unfollow = self.get_object()
        user = request.user

        if not user.following.filter(pk=user_to_unfollow.pk).exists():
            return Response({"error": "You are not following this user."}, status=status.HTTP_400_BAD_REQUEST)

        user.following.remove(user_to_unfollow)
        return Response({"detail": f"Successfully unfollowed {user_to_unfollow.username}."}, status=status.HTTP_200_OK)

class UserListView(generics.ListAPIView):
    """
    API view to list all users.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]