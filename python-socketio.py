import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.db import connection
import jwt

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            query_string = self.scope['query_string'].decode()
            self.room_name = query_string.split('&room_name=')[1].split('&')[0]

            token = query_string.split('token=')[1].split('&')[0]
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['user_id']

            # Retrieve user based on user_id asynchronously
            self.user = await self.get_user(user_id)
            if not self.user:
                await self.close(code=4003)
                return

            await self.accept()
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError, KeyError):
            await self.close(code=4002)

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    @database_sync_to_async
    def get_user(self, user_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_user WHERE id = %s", [user_id])
            row = cursor.fetchone()
            if row:
                user = {
                    'id': row[0],
                    'password': row[1],
                    'last_login': row[2],
                    'is_superuser': row[3],
                    'username': row[4],
                    'first_name': row[5],
                    'last_name': row[6],
                    'email': row[7],
                    'is_staff': row[8],
                    'is_active': row[9],
                    'date_joined': row[10],
                    'phone_number': row[11],
                    'security_question': row[12],
                    'security_answer': row[13],
                    'profile_picture': row[14],
                    'pin': row[15],
                    'status': row[16],
                    'groups': row[17],
                    'user_permissions': row[18],
                    'country': row[19],
                    'bio': row[20]
                    # Add more fields as needed
                }
                return user
            else:
                return None

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
