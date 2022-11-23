from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.html import format_html


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="user"
    )
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255, auto_created=True, blank=True)
    post_image = models.FileField(upload_to="images/", null=True, blank=True)
    like = models.ManyToManyField(User, related_name="like")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Automatically creates slug on save when you left slug empty"""
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.slug == self.title:
            self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="comment_user"
    )
    approve = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return format_html(f"Comment: {self.body} <br/> by <br/> {self.user}")
