from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, auto_created=True, blank=True)
    post_image = models.FileField(upload_to="images/", null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Automatically creates slug on save when you left slug empty"""
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.slug == self.title:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)
