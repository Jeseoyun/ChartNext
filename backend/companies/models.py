from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Company(models.Model):
    name = models.CharField(max_length=255)
    ticker = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class UserInterest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return f"{self.user.username} - {self.company.name}"

class StockPrice(models.Model):
    stock_code = models.CharField(max_length=20)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()
    
    class Meta:
        unique_together = ('stock_code', 'date')
        indexes = [
            models.Index(fields=['stock_code', 'date']),
        ]

class News(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'News'
        verbose_name_plural = 'News'

    def __str__(self):
        return self.title