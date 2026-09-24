from decimal import Decimal
from datetime import datetime, timedelta, timezone, date
from typing import List
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from ninja.security import HttpBearer
from core.models import Transaction, Category

api = NinjaAPI(title="JAST API", version="1.0.0")


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "access":
                return None
            user = User.objects.get(id=payload["user_id"])
            return user
        except (jwt.PyJWTError, User.DoesNotExist, KeyError):
            return None


auth = JWTAuth()


def _generate_token(user: User, token_type: str, lifetime: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user.id,
        "type": token_type,
        "exp": now + lifetime,
        "iat": now,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def generate_access_token(user: User) -> str:
    return _generate_token(user, "access", settings.JWT_ACCESS_TOKEN_LIFETIME)


def generate_refresh_token(user: User) -> str:
    return _generate_token(user, "refresh", settings.JWT_REFRESH_TOKEN_LIFETIME)


# Schemas
class RegisterIn(Schema):
    username: str
    password: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class LoginIn(Schema):
    username: str
    password: str


class RefreshIn(Schema):
    refresh_token: str


class RefreshOut(Schema):
    access_token: str


class UserOut(Schema):
    id: int
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class TokenOut(Schema):
    access_token: str
    refresh_token: str
    user: UserOut


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


class SuccessResponse(Schema):
    success: bool

class UserUpdateIn(Schema):
    username: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None


# Endpoints
@api.post("/auth/register", response=TokenOut)
def register(request, payload: RegisterIn):
    if User.objects.filter(username=payload.username).exists():
        raise HttpError(400, "Username already taken")

    user = User.objects.create_user(
        username=payload.username,
        password=payload.password,
        email=payload.email or "",
        first_name=payload.first_name or "",
        last_name=payload.last_name or "",
    )
    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user,
    }


@api.post("/auth/login", response=TokenOut)
def login_view(request, payload: LoginIn):
    user = authenticate(username=payload.username, password=payload.password)
    if user is None:
        raise HttpError(401, "Invalid username or password")

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user,
    }

@api.put("/auth/me", response=UserOut, auth=auth)
def update_current_user(request, payload: UserUpdateIn):
    user = request.auth

    if payload.username and payload.username != user.username:
        if User.objects.filter(username=payload.username).exclude(id=user.id).exists():
            raise HttpError(400, "Username already taken")
        user.username = payload.username

    if payload.email is not None:
        user.email = payload.email
    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.password:
        user.set_password(payload.password)

    user.save()
    return user


@api.delete("/auth/me", response=SuccessResponse, auth=auth)
def delete_current_user(request):
    user = request.auth
    user.delete()
    return {"success": True}


@api.post("/auth/refresh", response=RefreshOut)
def refresh_token_view(request, payload: RefreshIn):
    try:
        data = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        if data.get("type") != "refresh":
            raise HttpError(401, "Invalid token type")
        user = User.objects.get(id=data["user_id"])
        new_access_token = generate_access_token(user)
        return {"access_token": new_access_token}
    except (jwt.PyJWTError, User.DoesNotExist, KeyError):
        raise HttpError(401, "Invalid or expired refresh token")


@api.get("/auth/me", response=UserOut, auth=auth)
def get_current_user(request):
    return request.auth


@api.get("/transactions", response=List[TransactionOut], auth=auth)
def list_transactions(request):
    return (
        Transaction.objects.filter(user=request.auth)
        .select_related("category")
        .order_by("-date")
    )


@api.post("/transactions", response=TransactionOut, auth=auth)
def create_transaction(request, payload: TransactionIn):
    return Transaction.objects.create(
        user=request.auth,
        title=payload.title,
        amount=payload.amount,
        date=payload.date,
        category_id=payload.category_id,
    )


@api.put("/transactions/{transaction_id}", response=TransactionOut, auth=auth)
def update_transaction(request, transaction_id: int, payload: TransactionIn):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.auth)
    transaction.title = payload.title
    transaction.amount = payload.amount
    transaction.date = payload.date
    transaction.category_id = payload.category_id
    transaction.save()
    return transaction


@api.delete("/transactions/{transaction_id}", response=SuccessResponse, auth=auth)
def delete_transaction(request, transaction_id: int):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.auth)
    transaction.delete()
    return {"success": True}


@api.get("/categories", response=List[CategorySchema], auth=auth)
def list_categories(request):
    return Category.objects.all()
