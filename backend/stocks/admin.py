from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'market', 'exchange', 'sector', 'industry')
    list_filter = ('market', 'exchange', 'sector', 'industry')
    search_fields = ('name', 'code')
    ordering = ('name',)
