from .models import *
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # These are claims, you can add custom claims
        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['email'] = user.email
        token['bio'] = user.profile.bio
        token['role'] = user.profile.role
        token['image'] = str(user.profile.image)
        token['verified'] = user.profile.verified
        # ...
        return token

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     email = serializers.EmailField(source='user.email')

#     def validate(self, attrs):
#         data = super().validate(attrs)
#         # Add additional data to the response
#         data['email'] = self.user.email
#         return data

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     email = serializers.EmailField()

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Restrict the fields to accept only email and password during initialization
#         self.fields['email'] = serializers.EmailField()
#         self.fields['password'] = serializers.CharField()

#     def validate(self, attrs):
#         # Only accept email and password for authentication
#         email = attrs.get('email')
#         password = attrs.get('password')

#         if email and password:
#             user = authenticate(email=email, password=password)

#             if user:
#                 # If user authentication is successful, generate token
#                 data = super().validate(attrs)
#                 return data
#             else:
#                 raise serializers.ValidationError('Unable to log in with provided credentials.')
#         else:
#             raise serializers.ValidationError('Must include "email" and "password" fields.')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(max_length=200, required=True)
    first_name = serializers.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'phone', 'first_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone')  # Remove phone field from validated_data
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(
#         write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ('email', 'username', 'password', 'password2')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError(
#                 {"password": "Password fields didn't match."})

#         return attrs

#     def create(self, validated_data):
#         user = User.objects.create(
#             username=validated_data['username'],
#             email=validated_data['email']

#         )

#         user.set_password(validated_data['password'])
#         user.save()

#         return user