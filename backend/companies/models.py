from django.db import models
from django.conf import settings

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