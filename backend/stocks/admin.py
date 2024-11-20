from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'market', 'category', 'created_at')
    list_filter = ('market', 'category')
    search_fields = ('name', 'code')
    ordering = ('name',)
