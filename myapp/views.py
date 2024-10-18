from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import csrf_exempt
from myapp.forms import CustomSignupForm
from myapp.models import QuestionAnswer
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import UserChatHistory
from django.http import JsonResponse
import json
import logging
from .models import Conversation, Message
import uuid
import os
from groq import Groq
from .models import MyModel
from .forms import MyModelForm
import markdown  # Import markdown module
import bleach    # Import bleach for HTML sanitization

# Determine API key to use based on environment
GROQ_API_KEY = os.getenv('GROQ_API_KEY_DEV', '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')
if not os.getenv('GROQ_API_KEY_DEV'):
    GROQ_API_KEY = os.getenv('GROQ_API_KEY_PROD', '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')


# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

def my_view(request):
    # Fetch all objects from MongoDB
    data = MyModel.objects.using('mongodb').all()
    return render(request, 'myapp/template.html', {'data': data})

def index(request):
    """Render the main index page."""
    return render(request, 'myapp/index.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            # Log out the current session before logging in
            if request.user.is_authenticated:
                logout(request)
            
            login(request, user)
            
            # Redirect based on user role
            if user.is_superuser:
                return redirect('/admin/')  # Admin panel
            else:
                return redirect('user-dashboard')  # User panel
        else:
            return render(request, 'myapp/login.html', {'error': 'Invalid credentials'})
    else:
        return render(request, 'myapp/login.html')

def signup_view(request):
    """Handle user signup."""
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the new user
            user.is_active = True  # Ensure the user is active
            user.save()

            # Log the user in after signup
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('user-dashboard')  # Redirect to user dashboard after successful signup
        else:
            # If the form is not valid, display the errors on the form
            return render(request, 'myapp/signup.html', {'form': form})
    else:
        form = CustomSignupForm()

    return render(request, 'myapp/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')  # Redirect to main page with login and signup options

@csrf_exempt
def chatbot(request):
    """Handle chatbot interactions."""
    if request.method == 'POST':
        try:
            # Parse the incoming JSON request
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            user_message = data.get('message', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON format'}, status=400)

        # Check for a predefined answer in the database
        predefined_answer = get_predefined_answer(user_message)
        if predefined_answer:
            return JsonResponse({'message': predefined_answer})

        # Query the Groq API if no predefined answer is found
        groq_answer = query_groq_api(user_message)
        return JsonResponse({'message': groq_answer})

    return JsonResponse({'message': 'Invalid request method.'}, status=400)

def get_predefined_answer(user_message):
    """Retrieve a predefined answer from the database, if available."""
    try:
        # Look for a predefined answer in the database (case-insensitive match)
        question_answer = QuestionAnswer.objects.get(question__iexact=user_message)
        return question_answer.answer
    except QuestionAnswer.DoesNotExist:
        return None

def query_groq_api(user_message):
    """Query the Groq API using the provided user message."""
    try:
        # Query the Groq API using the SDK
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama3-8b-8192"  # Ensure the correct model is used
        )
        
        # Extract the content from the API response
        response_content = chat_completion.choices[0].message.content

        # Convert markdown to HTML with code highlighting
        html_content = markdown.markdown(
            response_content,
            extensions=[
                'fenced_code',
                'codehilite',
                'nl2br',
            ],
            extension_configs={
                'codehilite': {
                    'guess_lang': False,
                    'use_pygments': False,
                }
            },
            output_format='html5',
        )

        # Sanitize the HTML to prevent XSS attacks
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS.union({
            'p', 'pre', 'code', 'h1', 'h2', 'h3', 'h4',
            'ul', 'li', 'ol', 'strong', 'em', 'br', 'span'
        })

        allowed_attributes = bleach.sanitizer.ALLOWED_ATTRIBUTES.copy()
        allowed_attributes.update({
            '*': ['class', 'style'],
        })

        safe_html_content = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

        return safe_html_content
    
    except Exception as e:
        logging.error(f"Error querying Groq API: {e}")
        return "Sorry, I cannot answer that right now."

def create_object(request):
    if request.method == 'POST':
        form = MyModelForm(request.POST)
        if form.is_valid():
            # Save the object to MongoDB
            instance = form.save(commit=False)
            instance.save(using='mongodb')  # Saving to MongoDB
            return redirect('success')
    else:
        form = MyModelForm()

    return render(request, 'myapp/create_object.html', {'form': form})

def admin_required(user):
    return user.is_superuser

@user_passes_test(admin_required)
def admin_dashboard(request):
    """Render the admin dashboard."""
    return render(request, 'myapp/admin_page.html')

@login_required
def user_dashboard(request):
    user_email = request.user.email
    # Use the 'mongodb' alias to ensure the query is routed correctly
    recent_conversations = UserChatHistory.objects.using('mongodb').filter(user_email=user_email)

    context = {
        'recent_conversations': recent_conversations
    }
    return render(request, 'myapp/user_dashboard.html', context)



@login_required
def save_chat(request):
    """Save chat messages associated with a conversation."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            conversation_id = data.get('conversation_id')
            user_question = data.get('user_question', '')
            bot_response = data.get('bot_response', '')

            if not conversation_id:
                return JsonResponse({'status': 'error', 'message': 'No conversation ID provided'}, status=400)

            if user_question and bot_response:
                # Get or create the conversation
                conversation, created = Conversation.objects.get_or_create(
                    id=conversation_id,
                    defaults={'user': user}
                )

                # If the conversation is new, set its title to the first user message
                if created:
                    conversation.title = user_question[:50]  # Limit title length
                    conversation.save()

                # Save user message
                Message.objects.create(
                    conversation=conversation,
                    sender='user',
                    content=user_question
                )
                # Save bot response
                Message.objects.create(
                    conversation=conversation,
                    sender='bot',
                    content=bot_response
                )
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
        except Exception as e:
            logging.error(f"Error saving chat: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Failed to save chat'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def fetch_recent_conversations(request):
    """Fetch a list of recent conversations for the user."""
    user = request.user
    conversations = Conversation.objects.filter(user=user).order_by('-created_at')
    conversation_list = []
    for convo in conversations:
        conversation_list.append({
            'id': str(convo.id),
            'title': convo.title or f'Conversation {str(convo.id)[:8]}',
            'created_at': convo.created_at.isoformat(),
        })
    return JsonResponse({'status': 'success', 'conversations': conversation_list})

@login_required
def fetch_chat_history(request):
    """Fetch chat history for a specific conversation."""
    conversation_id = request.GET.get('conversation_id')
    user = request.user

    if not conversation_id:
        return JsonResponse({'status': 'error', 'message': 'No conversation ID provided'}, status=400)

    try:
        conversation = Conversation.objects.get(id=conversation_id, user=user)
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        chat_history = []
        for msg in messages:
            chat_history.append({
                'sender': msg.sender,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
            })
        return JsonResponse({'status': 'success', 'chat_history': chat_history})
    except Conversation.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Conversation not found'}, status=404)
    

    

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        message = json.loads(request.body).get('message')
        session_id = request.session.session_key  # Get session key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key

        # Save chat message with session ID
        chat_history = UserChatHistory.objects.create(
            session_id=session_id, message=message
        )
        chat_history.save()

        # Add logic to respond with appropriate chatbot message here
        return JsonResponse({'response': 'Message saved!'})
    

    

def index(request):
    return HttpResponse("<h1>Welcome to Sajilo Chat!</h1>")