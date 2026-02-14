"""
Security Views - 2FA, Password Reset, Password Update
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from .models import User
from .security_models import (
    TwoFactorOTP, UserSecuritySettings, PasswordHistory,
    PasswordResetToken, SecurityAuditLog
)
from .password_validators import validate_password_strength


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')[:500]


# ============== 2FA ENDPOINTS ==============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enable_2fa(request):
    """Enable two-factor authentication"""
    user = request.user
    method = request.data.get('method', 'email')
    
    if method not in ['email']:
        return Response(
            {'detail': 'Invalid 2FA method. Only "email" is supported.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get or create security settings
    settings_obj, _ = UserSecuritySettings.objects.get_or_create(user=user)
    
    # Send verification OTP first
    otp, code = TwoFactorOTP.generate_otp(user, get_client_ip(request))
    
    # Send OTP email
    try:
        send_mail(
            subject='Enable Two-Factor Authentication - AnalytiCore',
            message=f'''Hello {user.name},

You are enabling two-factor authentication on your AnalytiCore account.

Your verification code is: {code}

This code expires in 10 minutes.

If you did not request this, please secure your account immediately.

Best regards,
AnalytiCore Security Team
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
    except Exception as e:
        return Response(
            {'detail': f'Failed to send verification email: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response({
        'message': 'Verification code sent to your email',
        'otp_id': str(otp.otp_id)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_enable_2fa(request):
    """Verify OTP and enable 2FA"""
    user = request.user
    otp_id = request.data.get('otp_id')
    code = request.data.get('code')
    
    if not otp_id or not code:
        return Response(
            {'detail': 'OTP ID and code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        otp = TwoFactorOTP.objects.get(otp_id=otp_id, user=user)
    except TwoFactorOTP.DoesNotExist:
        return Response(
            {'detail': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    valid, message = otp.verify(code)
    
    if not valid:
        SecurityAuditLog.log_event(
            '2fa_failed', user, get_client_ip(request),
            get_user_agent(request), {'reason': message}
        )
        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
    
    # Enable 2FA
    settings_obj, _ = UserSecuritySettings.objects.get_or_create(user=user)
    settings_obj.two_factor_enabled = True
    settings_obj.two_factor_method = 'email'
    settings_obj.save()
    
    SecurityAuditLog.log_event(
        '2fa_enabled', user, get_client_ip(request), get_user_agent(request)
    )
    
    return Response({'message': 'Two-factor authentication enabled successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def disable_2fa(request):
    """Disable two-factor authentication"""
    user = request.user
    password = request.data.get('password')
    
    if not password:
        return Response(
            {'detail': 'Password is required to disable 2FA'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.check_password(password):
        return Response(
            {'detail': 'Invalid password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    settings_obj, _ = UserSecuritySettings.objects.get_or_create(user=user)
    settings_obj.two_factor_enabled = False
    settings_obj.two_factor_method = 'disabled'
    settings_obj.save()
    
    SecurityAuditLog.log_event(
        '2fa_disabled', user, get_client_ip(request), get_user_agent(request)
    )
    
    return Response({'message': 'Two-factor authentication disabled'})


@api_view(['POST'])
@permission_classes([AllowAny])
def send_login_otp(request):
    """Send OTP for login (when 2FA is enabled)"""
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'detail': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Don't reveal if user exists
        return Response({'message': 'If the account exists, an OTP has been sent'})
    
    # Check if 2FA is enabled
    try:
        security_settings = user.security_settings
        if not security_settings.two_factor_enabled:
            return Response(
                {'detail': '2FA is not enabled for this account'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except UserSecuritySettings.DoesNotExist:
        return Response(
            {'detail': '2FA is not enabled for this account'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Generate and send OTP
    otp, code = TwoFactorOTP.generate_otp(user, get_client_ip(request))
    
    try:
        send_mail(
            subject='Login Verification Code - AnalytiCore',
            message=f'''Hello {user.name},

Your login verification code is: {code}

This code expires in 10 minutes.

If you did not attempt to log in, please secure your account immediately.

Best regards,
AnalytiCore Security Team
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
    except Exception:
        pass  # Don't reveal email send failures
    
    return Response({
        'message': 'Verification code sent',
        'otp_id': str(otp.otp_id)
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login_otp(request):
    """Verify OTP and complete login"""
    otp_id = request.data.get('otp_id')
    code = request.data.get('code')
    
    if not otp_id or not code:
        return Response(
            {'detail': 'OTP ID and code are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        otp = TwoFactorOTP.objects.get(otp_id=otp_id)
    except TwoFactorOTP.DoesNotExist:
        return Response(
            {'detail': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    valid, message = otp.verify(code)
    
    if not valid:
        SecurityAuditLog.log_event(
            '2fa_failed', otp.user, get_client_ip(request),
            get_user_agent(request), {'reason': message}
        )
        return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create or get token
    token, _ = Token.objects.get_or_create(user=otp.user)
    
    # Update last login
    otp.user.last_login = timezone.now()
    otp.user.save(update_fields=['last_login'])
    
    # Reset login attempts
    try:
        otp.user.security_settings.reset_login_attempts()
    except UserSecuritySettings.DoesNotExist:
        pass
    
    SecurityAuditLog.log_event(
        '2fa_success', otp.user, get_client_ip(request), get_user_agent(request)
    )
    SecurityAuditLog.log_event(
        'login_success', otp.user, get_client_ip(request), get_user_agent(request)
    )
    
    return Response({
        'token': token.key,
        'user': {
            'user_id': str(otp.user.user_id),
            'email': otp.user.email,
            'name': otp.user.name,
            'is_verified': otp.user.is_verified,
            'is_staff': otp.user.is_staff
        }
    })


# ============== PASSWORD RESET ==============

@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """Request a password reset email"""
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'detail': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Always return success to prevent email enumeration
    response_message = 'If an account exists with this email, a reset link has been sent.'
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'message': response_message})
    
    # Create reset token
    token = PasswordResetToken.create_token(user, get_client_ip(request))
    
    # Build reset URL
    reset_url = f"{getattr(settings, 'APP_URL', 'https://analyticore.com')}/reset-password?token={token.token}"
    
    try:
        send_mail(
            subject='Password Reset Request - AnalytiCore',
            message=f'''Hello {user.name},

You have requested to reset your password for your AnalytiCore account.

Click the link below to reset your password:
{reset_url}

This link expires in 1 hour.

If you did not request this password reset, please ignore this email or contact support if you have concerns.

Best regards,
AnalytiCore Security Team
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        
        SecurityAuditLog.log_event(
            'password_reset_request', user, get_client_ip(request), get_user_agent(request)
        )
    except Exception:
        pass  # Don't reveal email send failures
    
    return Response({'message': response_message})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_token(request):
    """Verify if a reset token is valid"""
    token_str = request.data.get('token')
    
    if not token_str:
        return Response(
            {'detail': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = PasswordResetToken.objects.get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'valid': False, 'detail': 'Invalid or expired token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not token.is_valid():
        return Response(
            {'valid': False, 'detail': 'Token has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'valid': True,
        'email': token.user.email
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Reset password using token"""
    token_str = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not token_str or not new_password:
        return Response(
            {'detail': 'Token and new password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        token = PasswordResetToken.objects.get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'detail': 'Invalid or expired token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not token.is_valid():
        return Response(
            {'detail': 'Token has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = token.user
    
    # Validate password strength
    validation = validate_password_strength(new_password, user)
    if not validation['valid']:
        return Response(
            {'detail': 'Password does not meet requirements', 'errors': validation['errors']},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check password history
    if PasswordHistory.is_password_reused(user, new_password):
        return Response(
            {'detail': 'Cannot reuse any of your last 5 passwords'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update password
    user.set_password(new_password)
    user.save()
    
    # Add to password history
    PasswordHistory.add_password(user, user.password)
    
    # Update security settings
    settings_obj, _ = UserSecuritySettings.objects.get_or_create(user=user)
    settings_obj.set_password_expiry(days=90)
    
    # Mark token as used
    token.is_used = True
    token.save()
    
    # Invalidate all existing tokens
    Token.objects.filter(user=user).delete()
    
    SecurityAuditLog.log_event(
        'password_reset_complete', user, get_client_ip(request), get_user_agent(request)
    )
    
    return Response({'message': 'Password reset successfully. Please log in with your new password.'})


# ============== PASSWORD UPDATE ==============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_password(request):
    """Update password for authenticated user"""
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not current_password or not new_password:
        return Response(
            {'detail': 'Current password and new password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify current password
    if not user.check_password(current_password):
        return Response(
            {'detail': 'Current password is incorrect'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate new password strength
    validation = validate_password_strength(new_password, user)
    if not validation['valid']:
        return Response(
            {'detail': 'Password does not meet requirements', 'errors': validation['errors']},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check password history
    if PasswordHistory.is_password_reused(user, new_password):
        return Response(
            {'detail': 'Cannot reuse any of your last 5 passwords'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update password
    user.set_password(new_password)
    user.save()
    
    # Add to password history
    PasswordHistory.add_password(user, user.password)
    
    # Update security settings
    settings_obj, _ = UserSecuritySettings.objects.get_or_create(user=user)
    settings_obj.set_password_expiry(days=90)
    
    SecurityAuditLog.log_event(
        'password_change', user, get_client_ip(request), get_user_agent(request)
    )
    
    return Response({'message': 'Password updated successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_password(request):
    """Validate password strength without saving"""
    password = request.data.get('password', '')
    
    validation = validate_password_strength(password)
    
    return Response(validation)


# ============== SECURITY SETTINGS ==============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_security_settings(request):
    """Get user's security settings"""
    user = request.user
    settings_obj, _ = UserSecuritySettings.objects.get_or_create(user=user)
    
    return Response({
        'two_factor_enabled': settings_obj.two_factor_enabled,
        'two_factor_method': settings_obj.two_factor_method,
        'password_expires_at': settings_obj.password_expires_at,
        'password_expired': settings_obj.is_password_expired(),
        'force_password_change': settings_obj.force_password_change,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_security_audit_log(request):
    """Get user's security audit log"""
    user = request.user
    limit = int(request.query_params.get('limit', 20))
    
    logs = SecurityAuditLog.objects.filter(user=user).order_by('-created_at')[:limit]
    
    return Response({
        'logs': [{
            'event_type': log.event_type,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat(),
            'details': log.details
        } for log in logs]
    })
