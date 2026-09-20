from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views
from core.api import api  # Import your Django Ninja API instance

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    
    # Web App Views
    path('', views.home, name='home'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('stats/', views.stats, name='stats'),
    
    # Auth Views
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    
    # Django Ninja API
    path('api/', api.urls),
]
