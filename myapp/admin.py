from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from django.shortcuts import redirect
from .models import QuestionAnswer, UserInteraction, UserLoginData

# Custom AdminSite class
class MyAdminSite(AdminSite):
    site_header = 'My Admin Dashboard'  # Optional: Customize the admin site header
    site_title = 'Admin'  # Optional: Customize the admin site title

    def logout(self, request, extra_context=None):
        from django.contrib.auth import logout
        logout(request)
        return redirect('/admin/login/')  # Redirect to admin login page after logout

# Instantiate the custom admin site
admin_site = MyAdminSite(name='myadmin')

# Register your models with the custom admin site
@admin.register(QuestionAnswer, site=admin_site)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer')

@admin.register(UserInteraction, site=admin_site)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user_question', 'bot_response', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_question', 'bot_response')

@admin.register(UserLoginData, site=admin_site)
class UserLoginDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address')
    list_filter = ('login_time', 'user')
    search_fields = ('user__username', 'ip_address')
