import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_anonymous:
            self.close()
        else:
            self.group_name = str(self.scope["user"].pk)
            async_to_sync(self.channel_layer.group_add)(
                self.group_name, self.channel_name
            )
            self.accept()
            self.send(
                text_data=json.dumps(
                    {
                        "type": "connection established",
                        "message": f"connected with USER_PK: {self.group_name}",
                    }
                )
            )

    def disconnect(self, code):
        self.close()

    def notify(self, event):
        self.send(text_data=json.dumps(event["text"]))
