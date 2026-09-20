from ninja import NinjaAPI, Schema
from typing import List
from datetime import date
from decimal import Decimal
from core.models import Transaction, Category

api = NinjaAPI()

# --- Schemas (Data validation for Flutter) ---
class CategorySchema(Schema):
    id: int
    name: str

class TransactionOut(Schema):
    id: int
    title: str
    amount: Decimal
    date: date
    category: CategorySchema | None = None

class TransactionIn(Schema):
    title: str
    amount: Decimal
    date: date
    category_id: int | None = None

# --- Endpoints ---
@api.get("/transactions", response=List[TransactionOut])
def list_transactions(request):
    return Transaction.objects.select_related('category').all().order_by('-date')

@api.post("/transactions", response=TransactionOut)
def create_transaction(request, payload: TransactionIn):
    transaction = Transaction.objects.create(
        title=payload.title,
        amount=payload.amount,
        date=payload.date,
        category_id=payload.category_id
    )
    return transaction

@api.get("/categories", response=List[CategorySchema])
def list_categories(request):
    return Category.objects.all()
