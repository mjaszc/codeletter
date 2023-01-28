from django import template
from blog.models import Notification

register = template.Library()


@register.inclusion_tag("blog/notifications.html", takes_context=True)
def show_notifications(context):
    request_user = context.request.user
    notifications = Notification.objects.filter(
        receiver_user=request_user, is_seen=False
    )
    return {"notifications": notifications}
