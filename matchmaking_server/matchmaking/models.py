from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True)
    password = models.CharField(max_length=128)  # <-- Ajoute ce champ !
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class UserManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    managed_since = models.DateTimeField(auto_now_add=True)

class Game(models.Model):
    name = models.CharField(max_length=100) 
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Queue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip = models.CharField(max_length=45, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

class MatchConfig(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    config_json = models.TextField()  # JSON string for config
    created_at = models.DateTimeField(auto_now_add=True)

class Match(models.Model):
    player1 = models.ForeignKey(User, related_name='match_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(User, related_name='match_player2', on_delete=models.CASCADE)
    config = models.ForeignKey(MatchConfig, on_delete=models.SET_NULL, null=True, blank=True)
    board_state = models.CharField(max_length=9, default=" " * 9)
    is_finished = models.BooleanField(default=False)
    winner = models.CharField(max_length=10, null=True, blank=True)  # 'player1', 'player2', 'draw'
    created_at = models.DateTimeField(auto_now_add=True)

class Turn(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    move = models.CharField(max_length=10)  # e.g., "0,1"
    played_at = models.DateTimeField(auto_now_add=True)

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=100)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

class Statistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    games_played = models.IntegerField(default=0)
    games_won = models.IntegerField(default=0)
    games_lost = models.IntegerField(default=0)
    games_draw = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
