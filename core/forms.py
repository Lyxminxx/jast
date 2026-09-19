from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'category', 'date']
        # This widget forces the browser to show a date picker calendar
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
