from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('queue/', views.queue, name='queue'),
    path('join_queue/', views.join_queue, name='join_queue'),  # Ajout de la route pour join_queue
    path('matches/', views.matches, name='matches'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
]