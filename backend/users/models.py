from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 기본 필드만 사용
    pass

    class Meta:
        db_table = 'custom_user'