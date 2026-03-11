from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active', 'created_at']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email    = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    role     = serializers.ChoiceField(choices=['customer', 'staff', 'manager'])

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()