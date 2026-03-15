from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import os
import requests
from .models import User, EmailVerificationToken, GoogleAuthSession
from .serializers import (
    UserSerializer, UserRegistrationSerializer, 
    UserLoginSerializer, EmailVerificationSerializer
)
import logging

logger = logging.getLogger(__name__)

def send_verification_email(user, token):
    frontend_url = settings.CORS_ALLOWED_ORIGINS[0] if settings.CORS_ALLOWED_ORIGINS else 'http://localhost:3000'
    verification_link = f"{frontend_url}/verify-email?token={token.token}"
    
    html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
          <h2 style="color: #6366F1;">Welcome to AnalytiCore, {user.name}!</h2>
          <p>Thank you for signing up. Please verify your email address to get started.</p>
          <a href="{verification_link}" 
             style="display: inline-block; padding: 12px 24px; background-color: #6366F1; 
                    color: white; text-decoration: none; border-radius: 8px; margin: 20px 0;">
            Verify Email Address
          </a>
          <p>Or copy and paste this link into your browser:</p>
          <p style="color: #64748B; font-size: 14px;">{verification_link}</p>
          <p style="color: #94A3B8; font-size: 12px; margin-top: 30px;">
            If you didn't create this account, you can safely ignore this email.
          </p>
        </div>
      </body>
    </html>
    """
    
    send_mail(
        'Verify Your AnalytiCore Account',
        f'Please verify your account: {verification_link}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        user = result['user']
        token = result['token']
        
        try:
            send_verification_email(user, token)
        except Exception as e:
            # Don't delete the user on transient email failures
            # They can request a new verification email later
            logger.error("Failed to send verification email to %s: %s", user.email, str(e))
        
        return Response(
            {'message': 'Registration successful. Please check your email to verify your account.'},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.query_params.get('token')
    if not token:
        return Response({'detail': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = EmailVerificationSerializer(data={'token': token})
    if serializer.is_valid():
        token_obj = serializer.validated_data['token']
        user = token_obj.user
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        token_obj.is_used = True
        token_obj.save(update_fields=['is_used'])
        
        return Response({'message': 'Email verified successfully'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def google_auth_callback(request):
    session_id = request.query_params.get('session_id')
    if not session_id:
        return Response({'detail': 'Session ID required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        oauth_session_url = getattr(settings, 'OAUTH_SESSION_URL', None) or os.environ.get(
            'OAUTH_SESSION_URL',
            'https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data'
        )
        response = requests.get(
            oauth_session_url,
            headers={'X-Session-ID': session_id},
            timeout=10
        )
        
        if response.status_code != 200:
            return Response({'detail': 'Invalid session'}, status=status.HTTP_401_UNAUTHORIZED)
        
        data = response.json()
        
        user, created = User.objects.get_or_create(
            email=data['email'],
            defaults={
                'name': data['name'],
                'picture': data.get('picture'),
                'is_verified': True,
            }
        )
        
        if not created:
            user.picture = data.get('picture')
            user.save(update_fields=['picture'])
        
        GoogleAuthSession.objects.create(
            user=user,
            session_id=data['session_token'],
            google_id=data['id']
        )
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    
    except Exception as e:
        return Response(
            {'detail': f'Authentication failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    return Response(UserSerializer(request.user).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})