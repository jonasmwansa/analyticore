"""
Security Models - 2FA, Password Policy, Admin Alert Settings
"""
from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
import secrets
import hashlib
from datetime import timedelta


class TwoFactorOTP(models.Model):
    """Email OTP for two-factor authentication"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otp_codes'
    )
    otp_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=6)
    code_hash = models.CharField(max_length=64)  # SHA256 hash for security
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'two_factor_otp'
        indexes = [
            models.Index(fields=['user', 'is_used']),
            models.Index(fields=['otp_id']),
        ]
    
    @classmethod
    def generate_otp(cls, user, ip_address=None):
        """Generate a new 6-digit OTP"""
        # Invalidate any existing unused OTPs
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Generate secure 6-digit code
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        otp = cls.objects.create(
            user=user,
            code=code,
            code_hash=code_hash,
            expires_at=timezone.now() + timedelta(minutes=10),
            ip_address=ip_address
        )
        return otp, code
    
    def verify(self, code):
        """Verify the OTP code"""
        if self.is_used:
            return False, "OTP already used"
        
        if timezone.now() > self.expires_at:
            return False, "OTP expired"
        
        if self.attempts >= 3:
            self.is_used = True
            self.save()
            return False, "Too many attempts"
        
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        if code_hash != self.code_hash:
            self.attempts += 1
            self.save()
            return False, f"Invalid code. {3 - self.attempts} attempts remaining"
        
        self.is_used = True
        self.save()
        return True, "OTP verified"
    
    def __str__(self):
        return f"OTP for {self.user.email}"


class UserSecuritySettings(models.Model):
    """User-specific security settings"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_settings'
    )
    
    # 2FA Settings
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=20,
        choices=[('email', 'Email OTP'), ('disabled', 'Disabled')],
        default='disabled'
    )
    
    # Password Settings
    password_changed_at = models.DateTimeField(default=timezone.now)
    password_expires_at = models.DateTimeField(null=True, blank=True)
    force_password_change = models.BooleanField(default=False)
    
    # Login Security
    failed_login_attempts = models.IntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_security_settings'
    
    def is_locked_out(self):
        """Check if account is locked"""
        if self.lockout_until and timezone.now() < self.lockout_until:
            return True
        return False
    
    def record_failed_login(self):
        """Record a failed login attempt"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lockout_until = timezone.now() + timedelta(minutes=30)
        
        self.save()
    
    def reset_login_attempts(self):
        """Reset login attempts on successful login"""
        self.failed_login_attempts = 0
        self.lockout_until = None
        self.save()
    
    def is_password_expired(self):
        """Check if password has expired (90 days)"""
        if self.password_expires_at:
            return timezone.now() > self.password_expires_at
        return False
    
    def set_password_expiry(self, days=90):
        """Set password expiry date"""
        self.password_changed_at = timezone.now()
        self.password_expires_at = timezone.now() + timedelta(days=days)
        self.force_password_change = False
        self.save()
    
    def __str__(self):
        return f"Security settings for {self.user.email}"


class PasswordHistory(models.Model):
    """Track password history to prevent reuse"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_history'
    )
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'password_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    @classmethod
    def add_password(cls, user, password_hash):
        """Add password to history, keep last 5"""
        cls.objects.create(user=user, password_hash=password_hash)
        
        # Keep only last 5 passwords
        old_passwords = cls.objects.filter(user=user).order_by('-created_at')[5:]
        for old in old_passwords:
            old.delete()
    
    @classmethod
    def is_password_reused(cls, user, password):
        """Check if password was used in last 5 passwords"""
        from django.contrib.auth.hashers import check_password
        
        recent_passwords = cls.objects.filter(user=user).order_by('-created_at')[:5]
        for history in recent_passwords:
            if check_password(password, history.password_hash):
                return True
        return False
    
    def __str__(self):
        return f"Password history for {self.user.email}"


class PasswordResetToken(models.Model):
    """Token for password reset requests"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'password_reset_tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_used']),
        ]
    
    @classmethod
    def create_token(cls, user, ip_address=None):
        """Create a password reset token"""
        # Invalidate existing tokens
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        return cls.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=ip_address
        )
    
    def is_valid(self):
        """Check if token is valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"


class AdminAlertSettings(models.Model):
    """Admin-configurable alert thresholds"""
    # Singleton - only one instance
    
    # Error thresholds
    error_rate_threshold = models.FloatField(
        default=5.0,
        help_text="Alert when error rate exceeds this percentage"
    )
    db_response_threshold_ms = models.IntegerField(
        default=500,
        help_text="Alert when DB response exceeds this (milliseconds)"
    )
    max_errors_24h = models.IntegerField(
        default=10,
        help_text="Alert when errors in 24h exceed this count"
    )
    
    # Email settings
    alert_emails_enabled = models.BooleanField(default=True)
    daily_summary_enabled = models.BooleanField(default=True)
    
    # Additional recipients (comma-separated)
    additional_recipients = models.TextField(
        blank=True,
        help_text="Additional email addresses (comma-separated)"
    )
    
    # Check intervals
    health_check_interval_minutes = models.IntegerField(
        default=15,
        help_text="How often to run health checks"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'admin_alert_settings'
        verbose_name = 'Alert Settings'
        verbose_name_plural = 'Alert Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create singleton settings instance"""
        settings_obj, created = cls.objects.get_or_create(pk=1)
        return settings_obj
    
    def get_recipient_list(self):
        """Get list of additional recipients"""
        if not self.additional_recipients:
            return []
        return [email.strip() for email in self.additional_recipients.split(',') if email.strip()]
    
    def __str__(self):
        return "Admin Alert Settings"


class SecurityAuditLog(models.Model):
    """Audit log for security events"""
    EVENT_TYPES = [
        ('login_success', 'Successful Login'),
        ('login_failed', 'Failed Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Changed'),
        ('password_reset_request', 'Password Reset Requested'),
        ('password_reset_complete', 'Password Reset Completed'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('2fa_success', '2FA Verification Success'),
        ('2fa_failed', '2FA Verification Failed'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('settings_changed', 'Security Settings Changed'),
    ]
    
    log_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_audit_logs',
        null=True,
        blank=True
    )
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'security_audit_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['created_at']),
        ]
    
    @classmethod
    def log_event(cls, event_type, user=None, ip_address=None, user_agent='', details=None):
        """Create a security audit log entry"""
        return cls.objects.create(
            user=user,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
    
    def __str__(self):
        return f"{self.event_type} - {self.user.email if self.user else 'Anonymous'}"
