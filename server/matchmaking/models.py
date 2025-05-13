from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class Game(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

class Queue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Permet NULL
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    difficulty_level = models.IntegerField()
    joined_at = models.DateTimeField(auto_now_add=True)

class Match(models.Model):
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1_matches')
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2_matches')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    board_state = models.TextField(default='')  # État du plateau de jeu
    is_finished = models.BooleanField(default=False)
    winner = models.CharField(max_length=10, choices=[('player1', 'Player 1'), ('player2', 'Player 2'), ('draw', 'Draw')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Turn(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    played_by = models.CharField(max_length=10, choices=[('player1', 'Player 1'), ('player2', 'Player 2')])
    move_data = models.TextField()
    played_at = models.DateTimeField(auto_now_add=True)

class MatchConfig(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    config_data = models.TextField()

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

class Statistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    matches_played = models.IntegerField(default=0)
    matches_won = models.IntegerField(default=0)
    matches_lost = models.IntegerField(default=0)
    matches_drawn = models.IntegerField(default=0)

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(null=True, blank=True)