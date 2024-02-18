from django.shortcuts import render
import re

# rest-framework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

# User model & serializers
from django.contrib.auth.models import User
from api.serializers import UserSerializer, UserSerializerWithToken

# rest-framework-simplejwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# hashing-password
from django.contrib.auth.hashers import make_password

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


################################################################


# Login
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# Register a new user
@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'email', 'first-name', 'last-name', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'first-name': openapi.Schema(type=openapi.TYPE_STRING),
        'last-name': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
    }
))
@api_view(['POST'])
def registerUser(request):
    try:
        data = request.data

        # Check if password contains both letters, numbers, and has a minimum length of 8 characters
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).{8,}$', data['password']):
            return Response({'error': 'Password must contain both letters and numbers and be at least 8 characters long'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create a new user if not already exists
            user = User.objects.create(
                username=data['username'],
                first_name=data['first-name'],
                last_name=data['last-name'],
                email=data['email'],
                password=make_password(data['password']),
            )
            serializer = UserSerializerWithToken(user, many=False)
            return Response(serializer.data)

        except Exception as e:
            # Handle case where user with the same email or username already exists
            message = {'detail': 'User with this email or username already exists'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

    except KeyError:
        # Handle case where 'password' key is missing from request data
        return Response({'error': 'Password field is missing'}, status=status.HTTP_400_BAD_REQUEST)

    except:
        return Response('Unexpected error')

# User profile for User
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    try:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    except:
        return Response('Unexpected error')

# Update User Profile
@swagger_auto_schema(method='put', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'email', 'first-name', 'last-name', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'first-name': openapi.Schema(type=openapi.TYPE_STRING),
        'last-name': openapi.Schema(type=openapi.TYPE_STRING),
        'password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD),
    }
))
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    try:
        user = request.user
        serializer = UserSerializerWithToken(user, many=False)

        data = request.data

        # التحقق من صحة كلمة المرور وتحديثها
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).{8,}$', data['password']):
            return Response({'error': 'Password must contain both letters and numbers and be at least 8 characters long'},
             status=status.HTTP_400_BAD_REQUEST)
        user.password = make_password(data['password'])

        # تحديث الاسم الأول والاسم الأخير
        user.first_name = data['first-name']
        user.last_name = data['last-name']

        # تحقق من تغيير اسم المستخدم والبريد الإلكتروني
        try:
            if user.username != data['username']:
                if User.objects.filter(username=data['username']).exists():
                    return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
                user.username = data['username']
        except KeyError:
            pass  # إذا لم يتم تقديم 'username' في البيانات

        try:
            if user.email != data['email']:
                if User.objects.filter(email=data['email']).exists():
                    return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
                user.email = data['email']
        except KeyError:
            pass  # إذا لم يتم تقديم 'email' في البيانات

        user.save()
        return Response(serializer.data)

    except:
        return Response('Unexpected error')




@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    try:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    except:
        return Response('Unexpected error')

# Get User by id for Admin
@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    try:
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    except:
        return Response('Unexpected error')

# Update User by Admin
@swagger_auto_schema(method='put', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['username', 'email', 'first-name', 'last-name', 'password'],
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        'is-admin': openapi.Schema(type=openapi.TYPE_STRING),
    }
))
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateUser(request, pk):
    try:
        user = User.objects.get(id=pk)
        data = request.data

        # Update user fields if data exists
        user.is_staff = data['is-admin']

        # Update username and email if provided
        if 'username' in data:
            # Check if the new username is already taken
            if User.objects.filter(username=data['username']).exclude(id=pk).exists():
                return Response({'detail': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user.username = data['username']

        if 'email' in data:
            # Check if the new email is already taken
            if User.objects.filter(email=data['email']).exclude(id=pk).exists():
                return Response({'detail': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = data['email']

        user.save()

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

    except:
        return Response('Unexpected error')

# Delete User by Admin
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    try:
        user = User.objects.get(pk=pk)
        user.delete()
        return Response('User was deleted successfully')

    except:
        return Response('Unexpected error')