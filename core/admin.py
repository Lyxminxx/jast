from django.contrib import admin
from .models import Transaction, Category

admin.site.register(Category)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'title', 'amount', 'category')
    
    list_filter = ('category', 'date')
    
    search_fields = ('title',)
