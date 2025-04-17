import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message
from asgiref.sync import sync_to_async

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close() # Close connection if user is not authenticated
            return
        # Get user ID from URL parameters
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        try:
             # Get receiver user object asynchronously
            self.receiver = await self.get_user_by_id(self.user_id)
            self.receiver_username = self.receiver.username
            
            # Create room name based on user IDs (sorted to ensure consistency)
            user1_id = self.scope['user'].id
            user2_id = self.receiver.id
            self.room_group_name = f"chat_{''.join(sorted([str(user1_id), str(user2_id)]))}"
            
            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
        except:
            await self.close()

    @sync_to_async
    def get_user_by_id(self, user_id):
        return User.objects.get(id=user_id)
    
    @sync_to_async
    def get_receiver_user(self):
        return self.receiver
    
    # Leave room group
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)


    # Receive message from WebSocket
    async def receive_json(self, content):
        message = content['message']
        username = content['username']
        room_name = content['room_name']
        
        sender = self.scope['user']  # The currently authenticated user
        receiver = await self.get_receiver_user()
        
        # Save message to database
        await self.save_message(sender, receiver, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, 
            {
                "type": "chat_message", 
                "sender": sender.username, 
                "receiver": receiver.username,
                "message": message
            }
        )
        
     # outgoing message
    async def chat_message(self, event): 
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        # send message to WebSocket
        await self.send_json({
            'sender': sender,
            'receiver': receiver,
            'message': message
        })

    @sync_to_async
    def save_message(self, sender, receiver, message):
        Message.objects.create(sender=sender, receiver=receiver, content=message)

    