from rest_framework import serializers
from .notification_models import Notification, NotificationPreference, PushSubscription


class NotificationSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'notification_id', 'notification_type', 'title', 'message',
            'priority', 'related_project_id', 'related_object_type',
            'related_object_id', 'metadata', 'is_read', 'read_at',
            'created_at', 'time_ago'
        ]
        read_only_fields = ['notification_id', 'created_at']
    
    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff < timedelta(minutes=1):
            return 'Just now'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f'{minutes}m ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f'{hours}h ago'
        elif diff < timedelta(days=7):
            days = diff.days
            return f'{days}d ago'
        else:
            return obj.created_at.strftime('%b %d')


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_on_analysis_complete', 'email_on_data_issues',
            'email_on_export_ready', 'email_on_upload_complete',
            'email_on_pipeline_complete', 'email_on_pipeline_failed',
            'email_digest_frequency', 'push_enabled',
            'push_on_analysis_complete', 'push_on_data_issues',
            'push_on_export_ready', 'push_on_pipeline_complete',
            'push_on_pipeline_failed', 'inapp_enabled',
            'updated_at'
        ]
        read_only_fields = ['updated_at']


class PushSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushSubscription
        fields = ['subscription_id', 'endpoint', 'p256dh_key', 'auth_key', 'user_agent', 'is_active', 'created_at']
        read_only_fields = ['subscription_id', 'created_at']


class PushSubscriptionCreateSerializer(serializers.Serializer):
    endpoint = serializers.CharField()
    keys = serializers.DictField(child=serializers.CharField())
    
    def validate_keys(self, value):
        if 'p256dh' not in value or 'auth' not in value:
            raise serializers.ValidationError('Keys must include p256dh and auth')
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        endpoint = validated_data['endpoint']
        keys = validated_data['keys']
        
        # Update or create subscription
        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': user,
                'p256dh_key': keys['p256dh'],
                'auth_key': keys['auth'],
                'user_agent': self.context['request'].META.get('HTTP_USER_AGENT', ''),
                'is_active': True,
            }
        )
        return subscription
