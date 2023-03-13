from django import template
from blog.models import ProfileSettings


register = template.Library()


@register.filter(name="get_profile_image")
def get_profile_image(user):
    profile = ProfileSettings.objects.get_or_create(user=user)[0]
    if profile.image:
        return profile.image.url
    else:
        return None
