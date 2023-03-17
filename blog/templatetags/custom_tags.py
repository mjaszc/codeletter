from django import template
from blog.models import ProfileSettings, Notification

register = template.Library()


@register.filter(name="get_profile_image")
def get_profile_image(user):
    profile = ProfileSettings.objects.get_or_create(user=user)[0]
    if profile.image:
        return profile.image.url
    else:
        return None


@register.filter(name="unread_notifications")
def unread_notifications_count(user):
    if user.is_authenticated:
        return Notification.objects.filter(receiver_user=user, is_seen=False).count()
    return 0
