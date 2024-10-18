from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.contrib.auth.views import LogoutView, PasswordChangeView  # Import PasswordChangeView here

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('chatbot/', views.chatbot, name='chatbot'),
    # path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('password-change/', PasswordChangeView.as_view(), name='password_change'),  # Add this import
]

# Adding static files handling during development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
