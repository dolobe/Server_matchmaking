from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/matchmaking/$", consumers.MatchmakingConsumer.as_asgi()),
]