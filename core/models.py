from django.db import (
    models,
)
from django.utils import(
    timezone
)

class Transaction(models.Model):
    title = models.CharField(max_length=255)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    date = models.DateField(default=timezone.now)
    
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-date']

    @property
    def is_income(self):
        return self.amount > 0

    @property
    def is_expense(self):
        return self.amount < 0

    def __str__(self):
        return f"{self.date} | {self.title}: ${self.amount}"

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
