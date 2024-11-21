from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 기본 필드만 사용
    pass

    class Meta:
        db_table = 'custom_user'


class UserStock(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="stocks")
    stock = models.ForeignKey("stocks.Stock", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.stock.name}"