import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "notification"

        # joining group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"type": "connection established", "message": "connected"}
            )
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name,
        )

    # receive message from ws
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        event = {"type": "send_message", "message": message}

        # sending message to group
        await self.channel_layer.group_send(self.group_name, event)

    # receive message from group
    async def send_message(self, event):
        message = event["message"]

        # send message to ws
        await self.send(text_data=json.dumps({"message": message}))
