"""Notification API endpoints."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import AlertNotification


class NotificationListView(generics.ListAPIView):
    """GET /api/alerts/notifications/ — list user's notifications."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AlertNotification.objects.filter(user=self.request.user)[:50]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "level": n.level,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in queryset
        ]
        return Response({"code": 0, "message": "success", "data": data})


class NotificationMarkReadView(generics.GenericAPIView):
    """POST /api/alerts/notifications/{id}/read/ — mark notification as read."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk=None):
        try:
            notif = AlertNotification.objects.get(id=pk, user=request.user)
            notif.is_read = True
            notif.save(update_fields=["is_read"])
            return Response({"code": 0, "message": "已标记为已读"})
        except AlertNotification.DoesNotExist:
            return Response({"code": 1, "message": "通知不存在"}, status=404)


class NotificationMarkAllReadView(generics.GenericAPIView):
    """POST /api/alerts/notifications/read-all/ — mark all as read."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        AlertNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"code": 0, "message": "全部已读"})


class NotificationUnreadCountView(generics.GenericAPIView):
    """GET /api/alerts/notifications/unread-count/ — get unread count."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = AlertNotification.objects.filter(user=request.user, is_read=False).count()
        return Response({"code": 0, "message": "success", "data": {"count": count}})
