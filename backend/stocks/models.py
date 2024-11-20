from django.db import models


class Stock(models.Model):
    MARKET_CHOICES = [
        ("domestic", "국내"),
        ("international", "해외"),
    ]
    
    name = models.CharField(max_length=100)  # 종목명
    code = models.CharField(max_length=10, unique=True)  # 종목코드
    market = models.CharField(max_length=20, choices=MARKET_CHOICES)  # 국내/해외 구분
    category = models.CharField(max_length=50)  # 카테고리 (예: IT, 금융 등)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.market}"
