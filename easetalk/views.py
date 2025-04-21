from django.shortcuts import render, get_object_or_404, redirect
from therapy.models import Topic, SubTopic, TherapistProfile
from django.contrib import messages
from django.contrib.auth import get_user_model
from datetime import datetime
import random
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message
from django.utils import timezone

User = get_user_model()

# landing page view 
def index(request):
    return render(request, 'easetalk/index.html')

@login_required
def avatar_menu(request):
    therapist = None
 
    if hasattr(request.user, 'therapist'): 
        therapist = request.user.therapist
        
    # Create context to pass to the template
    context = {
        'therapist': therapist,
    }
    
    return render(request, 'easetalk/avatar_menu.html', context)

@login_required
def avatar_menu_close(request):
    """Return empty content to close the menu"""
    return render(request, 'easetalk/avatar_menu_close.html', {})

# get random therapist profile and display them 
def home_view(request): 
    if not request.user.is_authenticated:
        messages.error(request, 'You need to have an account before accessing this page')
        return redirect('easetalk:index') # leave for now 
    therapists = list(TherapistProfile.objects.order_by('-created_at'))
    random_therapists = random.sample(therapists, min(len(therapists), 15)) if therapists else []
    return render(request, 'easetalk/homepage.html', {'therapists': random_therapists})

# not implemented yet
# View to handle both topics and subtopics
def sidebar_view(request, topic_id=None, subtopic_id=None):
    topics = Topic.objects.all()  # Fetch all topics
    selected_topic = None
    subtopics = None
    therapists = None

    if topic_id:  # If a topic is selected
        selected_topic = get_object_or_404(Topic, id=topic_id)
        subtopics = selected_topic.subtopics.all()  # Retrieve subtopics related to the topic

    if subtopic_id and selected_topic:  # Ensure subtopic_id is related to the selected_topic
        subtopic = get_object_or_404(SubTopic, id=subtopic_id, topic=selected_topic)
        therapists = TherapistProfile.objects.filter(specializations__subtopics=subtopic)

    # Show random therapists if none are filtered
    if not therapists:
        therapists = list(TherapistProfile.objects.all())
        therapists = random.sample(therapists, min(len(therapists), 15))

    return render(request, 'easetalk/sidebar.html', {
        'topics': topics,
        'selected_topic': selected_topic,
        'subtopics': subtopics,  # Pass subtopics to the template
        'therapists': therapists,
    })


# view therapists that specialize in only specific fields
def therapist_specialization_view(request, specialization_name, template_name):
    therapists = TherapistProfile.objects.filter(specializations__name=specialization_name)
    #print(therapists)
    return render(request, template_name, {'therapists': therapists})


# a view to render the chat room page while retrieving chat messages, filtering messages, and displaying users
@login_required
def chat_room(request, user_id):
    try:
        chat_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('some_error_page')
    
    room_name = chat_user.username  # Still keep the room_name for templates
    search_query = request.GET.get('search', '')
    
    # Fetch chat messages between the logged-in user and the selected user
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=chat_user)) |
        (Q(receiver=request.user) & Q(sender=chat_user))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))

    chats = chats.order_by('timestamp')
    
    # Get all users with conversations
    users = User.objects.filter(
        Q(sent_messages__receiver=request.user) | 
        Q(received_messages__sender=request.user)
    ).distinct().exclude(id=request.user.id)
    
    user_last_messages = []

    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Sort user_last_messages safely
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.make_aware(datetime.min),
        reverse=True
    )

    return render(request, 'easetalk/chat.html', {
        'room_name': room_name,  # Keep for template compatibility
        'chat_user': chat_user,  # Add the actual user object
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query
    })