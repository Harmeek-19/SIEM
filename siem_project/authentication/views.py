from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.shortcuts import render
from .models import CustomUser
from .serializers import UserSerializer, LogoutSerializer, VerifyEmailSerializer, CustomTokenObtainPairSerializer
import logging

logger = logging.getLogger(__name__)

from rest_framework.authtoken.models import Token

class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        Token.objects.create(user=user)  # Create token for new user
        self.send_verification_email(user)

    # ... rest of the method remains the same
class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = self.request.build_absolute_uri(
            reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        subject = 'Verify your email for SIEM Tool'
        message = f"""
        Hello {user.first_name},

        Thank you for signing up for the SIEM Tool. To complete your registration, please verify your email by clicking the link below:

        {verification_link}

        If you did not sign up for this account, please ignore this email.

        Best regards,
        The SIEM Tool Team
        """
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            logger.info(f"User {request.user.username} logged out successfully")
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error during logout for user {request.user.username}: {str(e)}")
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyEmailSerializer

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return render(request, 'authentication/email_verification_result.html', {
                'title': 'Email Verification Successful',
                'message': 'Your email has been successfully verified.',
                'success': True
            })
        else:
            return render(request, 'authentication/email_verification_result.html', {
                'title': 'Email Verification Failed',
                'message': 'The verification link is invalid or has expired.',
                'success': False
            })

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]