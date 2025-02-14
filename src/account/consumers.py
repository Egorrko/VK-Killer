import json
import time
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from account.services import messages


class MessagesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.profile_id = self.scope['url_route']['kwargs']['profile_id']  # id пользователя, с кем переписка
        self.profile_user = await messages.get_user(self.profile_id)  # пользователь, с кем переписка
        self.dm = await messages.get_or_create_dm(self.user, self.profile_user)  # переписка
        self.dm_group_name = f'dm_{self.dm.id}'  # название ws канала к которому подключится собеседник

        # присоединиться к ws каналу
        await self.channel_layer.group_add(
            self.dm_group_name,
            self.channel_name
        )

        await self.accept()

        # await self.send(text_data=json.dumps(
        #     {'users': [{'id': self.user.id, 'name': self.user.username},
        #                {'id': self.profile_user.id, 'name': self.profile_user.username}]}
        # ))

    async def disconnect(self, _):
        # удалиться из ws канала
        await self.channel_layer.group_discard(
            self.dm_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data['type'] == 'messages_request':
            raw_msgs = await messages.get_messages(self.dm, data["last_msg_id"])
            msgs = await self.serialize_messages(raw_msgs)
            await self.send(text_data=json.dumps({'messages': msgs}))
        elif data['type'] == 'message':
            content = data['content']
            if not content or all([s == ' ' for s in content]): return  # пустое сообщение
            raw_msg = await messages.create(self.user, self.dm, content)
            msg = await self.serialize_messages([raw_msg])
            # отправить сообщение всем в ws канале
            await self.channel_layer.group_send(
                self.dm_group_name,
                {'type': 'send_new_message', 'data': msg}
            )

    async def send_new_message(self, event):
        # принять сообщение в ws канале и отправить его пользователю
        msg = event['data']
        await self.send(text_data=json.dumps({'messages': msg}))

    @sync_to_async
    def serialize_messages(self, messages) -> list[dict]:
        '''Сериализует список сообщений'''
        return [{'user': {'id': msg.user.id,
                          'username': msg.user.username,
                          'avatar': msg.user.avatar.url},
                 'message': {'id': msg.id,
                             'time': time.strftime("%H:%M", msg.timestamp.timetuple()),
                             'content': msg.message}} for msg in messages]
