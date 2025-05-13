from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Queue, Match, Turn, MatchConfig
from django.views.decorators.csrf import csrf_exempt
import json
from django.views import View

def home(request):
    return render(request, 'matchmaking/home.html')

@csrf_exempt
def queue(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        # Ajouter l'utilisateur à la file d'attente
        # (Remplacez cette logique par votre propre logique)
        return redirect('matches')
    return render(request, 'matchmaking/queue.html')

@csrf_exempt
def join_queue(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            # Vérifiez si l'utilisateur existe ou créez un utilisateur fictif
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(username=username)

            # Ajouter l'utilisateur à la file d'attente
            queue_entry = Queue.objects.create(user=user, game=None, difficulty_level=1)
            return JsonResponse({'status': 'success', 'queue_id': queue_entry.id})
        return JsonResponse({'status': 'error', 'message': 'Username is required.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def start_match(request, queue_id):
    if request.method == 'POST':
        # Logic to start a match based on the queue_id
        queue_entry = Queue.objects.get(id=queue_id)
        # Matchmaking logic here...
        match = Match.objects.create(player1=queue_entry, player2=None)  # Placeholder for player 2
        return JsonResponse({'status': 'success', 'match_id': match.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def play_turn(request, match_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        player = data.get('player')
        move = data.get('move')

        # Logic to process the turn
        match = Match.objects.get(id=match_id)
        turn = Turn.objects.create(match=match, player=player, move=move)
        # Check for win condition and update match status...

        return JsonResponse({'status': 'success', 'turn_id': turn.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def end_match(request, match_id):
    if request.method == 'POST':
        match = Match.objects.get(id=match_id)
        match.finished = True
        match.save()
        return JsonResponse({'status': 'success', 'message': 'Match ended.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def matches(request):
    matches = Match.objects.all()
    return render(request, 'matchmaking/matches.html', {'matches': matches})

def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return render(request, 'matchmaking/match_detail.html', {'match': match})

class QueueView(View):
    def get(self, request):
        # Exemple de réponse JSON pour tester la vue
        return JsonResponse({'message': 'Queue endpoint is working!'})

class MatchView(View):
    def get(self, request):
        # Exemple de réponse JSON pour tester la vue
        matches = list(Match.objects.values())
        return JsonResponse({'matches': matches})

    def post(self, request):
        # Exemple de logique pour créer un match
        return JsonResponse({'message': 'Match creation endpoint is working!'})

class TurnView(View):
    def get(self, request):
        # Exemple de réponse JSON pour tester la vue
        turns = list(Turn.objects.values())
        return JsonResponse({'turns': turns})

    def post(self, request):
        # Exemple de logique pour créer un tour
        return JsonResponse({'message': 'Turn creation endpoint is working!'})

class MatchConfigView(View):
    def get(self, request):
        # Exemple de réponse JSON pour tester la vue
        configs = list(MatchConfig.objects.values())
        return JsonResponse({'configs': configs})

    def post(self, request):
        # Exemple de logique pour créer une configuration de match
        return JsonResponse({'message': 'MatchConfig creation endpoint is working!'})