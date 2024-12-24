from django.shortcuts import render

# Create your views here.
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Author, Book, BorrowRecord
from .serializers import AuthorSerializer, BookSerializer, BorrowRecordSerializer, RegisterSerializer, LoginSerializer
import json

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class AuthorListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class AuthorDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookListCreateView(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer



class BorrowBookView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Borrow Book",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'book': openapi.Schema(type=openapi.TYPE_STRING, description='book number received after creating the book.'),
                'borrowed_by': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the borrower'),
            },
            required=['book', 'borrowed_by'],
        ),
        responses={
            200: openapi.Response(
                description="Book is borrowed on successful attempt.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, description='Borrowing id of the book'),
                        'borrowed_by': openapi.Schema(type=openapi.TYPE_STRING, description='User name of the borrower'),
                        'borrow_date': openapi.Schema(type=openapi.TYPE_STRING, description='Borrow Date'),
                        'return_date': openapi.Schema(type=openapi.TYPE_STRING, description='Return date gets populated after the borrower returns the book'),
                        'book': openapi.Schema(type=openapi.TYPE_STRING, description='Book id of the book.')
                    },
                )
            ),
            401: "Invalid credentials",
            400: "borrowed_by and book are required",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = BorrowRecordSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.validated_data['book']
            if book.available_copies > 0:
                book.available_copies -= 1
                book.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "No copies available"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReturnBookView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def put(self, request, id, *args, **kwargs):
        try:
            record = BorrowRecord.objects.get(id=id, return_date__isnull=True)
            record.return_date = request.data.get('return_date')
            record.save()
            record.book.available_copies += 1
            record.book.save()
            return Response({"message": "Book returned successfully"}, status=status.HTTP_200_OK)
        except BorrowRecord.DoesNotExist:
            return Response({"error": "Invalid record or already returned"}, status=status.HTTP_400_BAD_REQUEST)


import os
from .tasks import generate_report_task

class ReportView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        reports_dir = os.path.join(os.getcwd(), "reports")
        if not os.path.exists(reports_dir) or not os.listdir(reports_dir):
            return Response({"error": "No reports available"}, status=status.HTTP_404_NOT_FOUND)
        latest_report = max(
            [os.path.join(reports_dir, f) for f in os.listdir(reports_dir)],
            key=os.path.getctime,
        )
        # Read and return the report
        with open(latest_report, 'r') as file:
            report_data = json.load(file)

        return Response(report_data)

    def post(self, request, *args, **kwargs):
        task = generate_report_task.delay()
        return Response({"message": "Report generation started", "task_id": task.id}, status=status.HTTP_202_ACCEPTED)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Register users",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='email of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
            },
            required=['username', 'password'],
        ),
        responses={
            200: openapi.Response(
                description="User created on successful attempt.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='User registered successfully'),
                    },
                )
            ),
            401: "Invalid credentials",
            400: "Username, email and password are required",
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Login user to obtain JWT tokens.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
            },
            required=['username', 'password'],
        ),
        responses={
            200: openapi.Response(
                description="Tokens returned on successful login",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                    },
                )
            ),
            401: "Invalid credentials",
            400: "Username and password are required",
        }
    )
    def post(self, request, *args, **kwargs):
        
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
            )
            print("username: ",user.username)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)