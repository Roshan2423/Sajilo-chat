from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
import uuid

# Model to store predefined question-answer pairs
class QuestionAnswer(models.Model):
    question = models.CharField(max_length=255, validators=[MaxLengthValidator(255)], unique=True)  # Ensures unique questions
    answer = models.TextField(verbose_name="Answer")

    class Meta:
        verbose_name = "Question Answer"
        verbose_name_plural = "Question Answers"
        ordering = ['question']  # Optional ordering by question

    def __str__(self):
        return self.question


# Model to store user interactions with the chatbot
class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Track user who asked the question
    user_question = models.CharField(max_length=255)
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Interaction"
        verbose_name_plural = "User Interactions"

    def __str__(self):
        return self.user_question


# Model to track user login data
class UserLoginData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


# Model to store social media authentication tokens
class SocialToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)  # Added unique constraint
    token_secret = models.CharField(max_length=255, default='', blank=True)  # Allow blank values

    # Optional: Add a JSONField for additional token data
    # extra_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.token


class MyModel(models.Model):
    # Define your fields here
    name = models.CharField(max_length=100)
    description = models.TextField()

class UserChatHistory(models.Model):
    user_email = models.EmailField()
    chat_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "userchathistory"
        # managed = False  # Ensure Django does not try to migrate this model

    def __str__(self):
        return f"Chat by {self.user_email} on {self.timestamp}"
    


    # New model for conversation management
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Conversation {str(self.id)[:8]}"

# New model for messages within a conversation
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.CharField(max_length=10)  # 'user' or 'bot'
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} message at {self.timestamp}"