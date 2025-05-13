from django.urls import path
from matchmaking import views

urlpatterns = [
    path('api/matchmaking/', views.MatchmakingView.as_view(), name='matchmaking'),
    path('api/matchmaking/queue/', views.QueueView.as_view(), name='queue'),
    path('api/matchmaking/match/', views.MatchView.as_view(), name='match'),
    path('api/matchmaking/turn/', views.TurnView.as_view(), name='turn'),
]