from django.urls import path
from . import views_notification

urlpatterns = [
    path("", views_notification.NotificationListView.as_view(), name="notification-list"),
    path("<int:pk>/read/", views_notification.NotificationMarkReadView.as_view(), name="notification-mark-read"),
    path("read-all/", views_notification.NotificationMarkAllReadView.as_view(), name="notification-mark-all-read"),
    path("unread-count/", views_notification.NotificationUnreadCountView.as_view(), name="notification-unread-count"),
]
