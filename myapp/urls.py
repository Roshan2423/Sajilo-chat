from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('save_chat/', views.save_chat, name='save_chat'),
    path('fetch_chat_history/', views.fetch_chat_history, name='fetch_chat_history'),
    path('fetch_recent_conversations/', views.fetch_recent_conversations, name='fetch_recent_conversations'),
    path('user-dashboard/', views.user_dashboard, name='user-dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('logout/', views.logout_view, name='logout'),  # Updated to use custom logout view
]
