from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core.api import api  # Import your Django Ninja API instance

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    # Django Ninja API
    path('api/', api.urls),
]
