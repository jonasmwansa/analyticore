from django.urls import path
from . import views, security_views

app_name = 'users'

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('verify-email', views.verify_email, name='verify-email'),
    path('session', views.google_auth_callback, name='google-auth'),
    path('me', views.get_me, name='me'),
    path('logout', views.logout, name='logout'),
    
    # 2FA Endpoints
    path('2fa/enable', security_views.enable_2fa, name='2fa-enable'),
    path('2fa/verify-enable', security_views.verify_enable_2fa, name='2fa-verify-enable'),
    path('2fa/disable', security_views.disable_2fa, name='2fa-disable'),
    path('2fa/send-otp', security_views.send_login_otp, name='2fa-send-otp'),
    path('2fa/verify-otp', security_views.verify_login_otp, name='2fa-verify-otp'),
    
    # Password Reset
    path('password/reset-request', security_views.request_password_reset, name='password-reset-request'),
    path('password/verify-token', security_views.verify_reset_token, name='password-verify-token'),
    path('password/reset', security_views.reset_password, name='password-reset'),
    path('password/update', security_views.update_password, name='password-update'),
    path('password/validate', security_views.validate_password, name='password-validate'),
    
    # Security Settings
    path('security/settings', security_views.get_security_settings, name='security-settings'),
    path('security/audit-log', security_views.get_security_audit_log, name='security-audit-log'),
]