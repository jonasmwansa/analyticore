from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.conf import settings

from .notification_models import Notification, NotificationPreference, PushSubscription
from .notification_serializers import (
    NotificationSerializer, NotificationPreferenceSerializer,
    PushSubscriptionSerializer, PushSubscriptionCreateSerializer
)
from .notification_service import NotificationService


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """Get user's notifications with pagination"""
    queryset = Notification.objects.filter(user=request.user)
    
    # Filter by read status
    is_read = request.query_params.get('is_read')
    if is_read is not None:
        queryset = queryset.filter(is_read=is_read.lower() == 'true')
    
    # Filter by type
    notification_type = request.query_params.get('type')
    if notification_type:
        queryset = queryset.filter(notification_type=notification_type)
    
    paginator = NotificationPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = NotificationSerializer(page, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notification_summary(request):
    """Get notification summary (unread count, etc.)"""
    unread_count = NotificationService.get_unread_count(request.user)
    
    # Get latest 5 unread notifications
    latest_unread = Notification.objects.filter(
        user=request.user, 
        is_read=False
    )[:5]
    
    return Response({
        'unread_count': unread_count,
        'latest_unread': NotificationSerializer(latest_unread, many=True).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    notification = NotificationService.mark_as_read(notification_id, request.user)
    
    if not notification:
        return Response(
            {'detail': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    return Response(NotificationSerializer(notification).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read"""
    count = NotificationService.mark_all_as_read(request.user)
    return Response({'marked_count': count})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        notification = Notification.objects.get(
            notification_id=notification_id,
            user=request.user
        )
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response(
            {'detail': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_preferences(request):
    """Get or update notification preferences"""
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        return Response(NotificationPreferenceSerializer(prefs).data)
    
    serializer = NotificationPreferenceSerializer(prefs, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_push(request):
    """Subscribe to push notifications"""
    serializer = PushSubscriptionCreateSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        subscription = serializer.save()
        
        # Enable push in preferences
        prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
        prefs.push_enabled = True
        prefs.save(update_fields=['push_enabled'])
        
        return Response(
            PushSubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unsubscribe_push(request):
    """Unsubscribe from push notifications"""
    endpoint = request.data.get('endpoint')
    
    if not endpoint:
        return Response(
            {'detail': 'Endpoint is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    deleted, _ = PushSubscription.objects.filter(
        user=request.user,
        endpoint=endpoint
    ).delete()
    
    if deleted:
        # Check if user has any remaining subscriptions
        remaining = PushSubscription.objects.filter(user=request.user, is_active=True).exists()
        if not remaining:
            NotificationPreference.objects.filter(user=request.user).update(push_enabled=False)
    
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vapid_public_key(request):
    """Get VAPID public key for push notification subscription"""
    vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
    
    if not vapid_public_key:
        return Response(
            {'detail': 'Push notifications not configured'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response({'public_key': vapid_public_key})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """Send a test notification (for debugging)"""
    notification_type = request.data.get('type', 'system')
    
    notification = NotificationService.create_notification(
        user=request.user,
        notification_type=notification_type,
        title='Test Notification',
        message='This is a test notification to verify your notification settings are working correctly.',
        priority='low',
        send_email=request.data.get('send_email', False),
        send_push=request.data.get('send_push', False),
    )
    
    return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
