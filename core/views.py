from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Transaction
from .forms import TransactionForm, CustomUserCreationForm
import json
from datetime import timedelta
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('home')
    else:
        form = TransactionForm()

    transactions = Transaction.objects.filter(user=request.user)
    total_balance = transactions.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'form': form,
        'transactions': transactions,
        'total_balance': total_balance,
    }
    return render(request, 'home.html', context)

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'edit.html', {'form': form, 'transaction': transaction})

@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
    return redirect('home')

@login_required
def stats(request):
    time_filter = request.GET.get('filter', 'all')
    now = timezone.now().date()
    
    expenses = Transaction.objects.filter(user=request.user, amount__lt=0)
    
    if time_filter == 'week':
        expenses = expenses.filter(date__gte=now - timedelta(days=7))
    elif time_filter == 'month':
        expenses = expenses.filter(date__gte=now - timedelta(days=30))
    elif time_filter == 'year':
        expenses = expenses.filter(date__gte=now - timedelta(days=365))
        
    category_data = expenses.values('category__name').annotate(total=Sum('amount'))
    
    labels = []
    data = []
    for item in category_data:
        cat_name = item['category__name'] or 'Uncategorized'
        labels.append(cat_name)
        data.append(abs(float(item['total'])))
        
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'current_filter': time_filter,
    }
    return render(request, 'stats.html', context)
