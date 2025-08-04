# myapp/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/animal-records', consumers.AnimalRecordConsumer.as_asgi()),
]
