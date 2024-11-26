from django.db import models
from django.conf import settings

class NewsArticle(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    category = models.CharField(max_length=255)
    title = models.TextField()
    url = models.URLField(max_length=1024, unique=True)
    authors = models.JSONField(null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class NewsImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    refid = models.IntegerField()
    src = models.TextField()
    caption = models.TextField(null=True, blank=True)
    article = models.ForeignKey(NewsArticle, related_name='images', on_delete=models.CASCADE)

    def __str__(self):
        return f"Image {self.refid} for {self.article.title}"

class NewsContent(models.Model):
    id = models.BigAutoField(primary_key=True)
    refid = models.IntegerField()
    text = models.TextField()
    article = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='contents')

    def __str__(self):
        return f"Content {self.refid} for {self.article.title}"

class Comment(models.Model):
    article = models.ForeignKey(NewsArticle, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"
