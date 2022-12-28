import json
from channels.generic.websocket import WebsocketConsumer


class NotificationConsumer(WebsocketConsumer):
    def connect(self):

        self.accept()
        self.send(
            text_data=json.dumps({"type": "Connected", "message": "Now connected."})
        )

    def receive(self, data):
        print(data)
        self.send(text_data=json.dumps({"status": "received"}))
