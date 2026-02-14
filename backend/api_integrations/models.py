"""
Models for API integrations including OAuth tokens
"""
from django.db import models
from django.conf import settings
import uuid


class GoogleSheetsToken(models.Model):
    """Store Google Sheets OAuth tokens per user"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='google_sheets_token'
    )
    
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.CharField(max_length=255, default="https://oauth2.googleapis.com/token")
    expires_at = models.DateTimeField()
    scopes = models.JSONField(default=list)
    
    # User info from Google
    google_email = models.EmailField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'google_sheets_tokens'
    
    def __str__(self):
        return f"Google Sheets Token for {self.user.email}"
    
    def to_dict(self):
        """Convert to dictionary for use with Google API client"""
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_uri': self.token_uri,
            'expires_at': self.expires_at,
            'scopes': self.scopes
        }
    
    def update_access_token(self, new_token):
        """Update access token after refresh"""
        self.access_token = new_token
        self.save(update_fields=['access_token', 'updated_at'])
