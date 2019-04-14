from channels.generic.websocket import AsyncWebsocketConsumer
import json


class ChatConsumer(AsyncWebsocketConsumer):

    async def user_rooms_append(self):
        user = self.scope['user']
        if user.is_authenticated:
            index = self.channel_layer.consistent_hash(self.room_group_name)
            async with self.channel_layer.connection(index) as connection:
                groups_key = 'chats:{}:groups'.format(user.username)
                await connection.sadd(groups_key, self.room_group_name)

    async def user_rooms_list(self):
        result = []
        user = self.scope['user']
        if user.is_authenticated:
            index = self.channel_layer.consistent_hash(self.room_group_name)
            async with self.channel_layer.connection(index) as connection:
                groups_key = 'chats:{}:groups'.format(user.username)
                result = [x.decode('utf-8') for x in await connection.smembers(groups_key)]
        return result

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.user_rooms_append()
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        username = user.username if user.is_authenticated else 'default'
        for room in await self.user_rooms_list():
            is_notify = 'chat_message' if self.room_group_name == room else 'notification'
            await self.channel_layer.group_send(
                room,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'is_notify': is_notify,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        is_notify = event['is_notify']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': event['username'],
            'is_notify': is_notify,
        }))
