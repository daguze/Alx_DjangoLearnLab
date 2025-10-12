from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import CoustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoustomUser
        fields = ['id', 'username', 'email', 'bio', 'profile_picture', 'followers']
        read_only_fields = ['id', 'followers']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CoustomUser
        fields = ['id', 'username', 'email', 'password', 'bio', 'profile_picture']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = CoustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            bio=validated_data.get('bio', ''),
            profile_picture=validated_data.get('profile_picture', None)
        )
        Token.objects.create(user=user)
        return user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            try:
                user = CoustomUser.objects.get(username=username)
            except CoustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid username or password")

            if not user.check_password(password):
                raise serializers.ValidationError("Invalid username or password")
        else:
            raise serializers.ValidationError("Both username and password are required")

        data['user'] = user
        return data
    