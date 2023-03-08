from blog.models import ProfileSettings


def profile_image(request):
    profile_image = None
    if request.user.is_authenticated:
        profile_settings = ProfileSettings.objects.filter(user=request.user)[0]
        if profile_settings:
            profile_image = profile_settings.image.url
    return {"profile_image": profile_image}
