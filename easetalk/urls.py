from django.urls import path
from . import views

app_name = 'easetalk'

urlpatterns = [
    path('', views.index, name='index'), 
    path('avatar-menu/', views.avatar_menu, name='avatar_menu'),
    path('avatar-menu-close/', views.avatar_menu_close, name='avatar_menu_close'),
    path('home/', views.home_view, name='home'),  
    path('sidebar/', views.sidebar_view, name='sidebar_view'),
    path('sidebar/<int:topic_id>/', views.sidebar_view, name='sidebar_view'), # points to the subtopic that is related to that topic id
    path('sidebar/<int:topic_id>/<int:subtopic_id>/', views.sidebar_view, name='sidebar_view'), #
    path('mentalhealth/', views.therapist_specialization_view, {'specialization_name': 'Mental Health', 
    'template_name': 'easetalk/mentalhealth.html'}, name='mental_health'), # url to get mental health therapist
    path('relationship/', views.therapist_specialization_view, {'specialization_name': 'Relationships', 
    'template_name': 'easetalk/relationship.html'}, name='relationship'), # url to get relationships therapist
    path('trauma/', views.therapist_specialization_view, {'specialization_name': 'Trauma & Abuse', 
    'template_name': 'easetalk/trauma&abuse.html'}, name='trauma'), # url to get Trauma & Abuse therapist
    path('Self-Esteem/', views.therapist_specialization_view, {'specialization_name': 'Self-Esteem & Self-Worth', 
    'template_name': 'easetalk/self-esteem&self-worth.html'}, name='selfesteem'), # url to get Self-Esteem & Self-Worth therapist
    path('spirituality/', views.therapist_specialization_view, {'specialization_name': 'Spirituality', 
    'template_name': 'easetalk/spirituality.html'}, name='spirituality'), # url to get Spirituality therapist
    path('addiction/', views.therapist_specialization_view, {'specialization_name': 'Addiction & Recovery', 
    'template_name': 'easetalk/addiction.html'}, name='addiction'), # url to get Spirituality therapist
    path('chats/<int:user_id>/', views.chat_room, name='chats') # represent the other user, username in the chat room
]
