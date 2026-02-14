from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('verify-email', views.verify_email, name='verify-email'),
    path('session', views.google_auth_callback, name='google-auth'),
    path('me', views.get_me, name='me'),
    path('logout', views.logout, name='logout'),
]