from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Transaction
from .forms import TransactionForm
import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum


def home(request):
    # 1. Handle form submission
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home') # Refresh the page
    else:
        form = TransactionForm()

    # 2. Fetch data for the table
    transactions = Transaction.objects.all()
    
    # Calculate total balance (returns 0 if database is empty)
    total_balance = transactions.aggregate(Sum('amount'))['amount__sum'] or 0

    # 3. Send data to the template
    context = {
        'form': form,
        'transactions': transactions,
        'total_balance': total_balance,
    }
    return render(request, 'home.html', context)

def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TransactionForm(instance=transaction)
        
    return render(request, 'edit.html', {'form': form, 'transaction': transaction})

def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
    return redirect('home')

def stats(request):
    # 1. Figure out what time period we are looking at
    time_filter = request.GET.get('filter', 'all')
    now = timezone.now().date()
    
    # Start with only expenses (numbers less than 0)
    expenses = Transaction.objects.filter(amount__lt=0)
    
    # 2. Filter by date based on the button clicked
    if time_filter == 'week':
        expenses = expenses.filter(date__gte=now - timedelta(days=7))
    elif time_filter == 'month':
        expenses = expenses.filter(date__gte=now - timedelta(days=30))
    elif time_filter == 'year':
        expenses = expenses.filter(date__gte=now - timedelta(days=365))
        
    # 3. Group by category and sum the amounts
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    
    # 4. Format data for Chart.js
    labels = []
    data = []
    
    for item in category_data:
        # If category is null, call it 'Uncategorized'
        cat_name = item['category__name'] or 'Uncategorized'
        labels.append(cat_name)
        # Make the number positive for the chart (so it draws correctly)
        data.append(abs(float(item['total'])))
        
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'current_filter': time_filter,
    }
    return render(request, 'stats.html', context)
