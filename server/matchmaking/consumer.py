import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Match, User, Game

class MatchmakingConsumer(AsyncWebsocketConsumer):
    queue = []  # File d'attente des joueurs

    async def connect(self):
        print("WebSocket connected")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"WebSocket disconnected with code {close_code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(f"Message received: {data}")
        await self.send(text_data=json.dumps({
            'message': 'Message received',
            'data': data
        }))

        from .models import Match, User, Game  # Importez les modèles ici
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'join_queue':
            username = data.get('username')
            if not username:
                await self.send(text_data=json.dumps({
                    'error': 'Username is required to join the queue'
                }))
                return

            # Vérifiez si l'utilisateur existe
            try:
                user = await sync_to_async(User.objects.get)(username=username)
            except User.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'error': f'User {username} does not exist'
                }))
                return

            self.queue.append(username)
            print(f"Current queue: {self.queue}")
            await self.send(text_data=json.dumps({
                'message': f'{username} joined the queue.',
                'queue': self.queue
            }))

            # Si deux joueurs sont dans la file, créer un match
            if len(self.queue) >= 2:
                print("Two players found in the queue. Creating a match...")
                player1_username = self.queue.pop(0)
                player2_username = self.queue.pop(0)
                print(f"Player 1: {player1_username}, Player 2: {player2_username}")

                # Récupérer les utilisateurs depuis la base de données
                player1 = await sync_to_async(User.objects.get)(username=player1_username)
                player2 = await sync_to_async(User.objects.get)(username=player2_username)
                
                # Récupérer le premier jeu disponible
                game = await sync_to_async(Game.objects.first)()
                print(f"Game selected: {game.name if game else 'None'}")
                if not game:
                    await self.send(text_data=json.dumps({
                        'error': 'No game available to create a match'
                    }))
                    return

                # Créer un match dans la base de données
                match = await sync_to_async(Match.objects.create)(
                    player1=player1,
                    player2=player2,
                    game=game,
                    board_state='---------',  # Plateau vide pour le morpion
                )

                print(f"Match created: {match.id}, Player1: {player1.username}, Player2: {player2.username}")

                await self.send(text_data=json.dumps({
                    'action': 'match_created',
                    'message': f'Match created between {player1.username} and {player2.username}!',
                    'match_id': match.id,
                    'player': 'player1' if player1.username == username else 'player2'
                }))
                print(f"Match created message sent to clients: Match ID {match.id}")
        elif action == 'leave_queue':
            username = data.get('username')
            if username in self.queue:
                self.queue.remove(username)
                await self.send(text_data=json.dumps({
                    'message': f'{username} left the queue.',
                    'queue': self.queue
                }))
            else:
                await self.send(text_data=json.dumps({
                    'error': f'{username} is not in the queue'
                }))
        elif action == 'play_turn':
            match_id = data.get('match_id')
            player = data.get('player')  # 'player1' ou 'player2'
            move = data.get('move')  # Position du coup (0-8 pour le morpion)

            print(f"Looking for match with ID: {match_id}")

            try:
                # Utilisez sync_to_async pour les opérations de base de données
                match = await sync_to_async(Match.objects.get)(id=match_id)
            except Match.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'error': 'Match not found'
                }))
                return

            # Vérifiez si le match est terminé
            if match.is_finished:
                await self.send(text_data=json.dumps({
                    'error': 'Match is already finished'
                }))
                return

            # Mettre à jour l'état du plateau
            board = list(match.board_state)
            if board[move] == '-':
                board[move] = 'X' if player == 'player1' else 'O'
                match.board_state = ''.join(board)

                # Vérifiez si le match est terminé
                winner = check_winner(board)
                if winner:
                    match.is_finished = True
                    match.winner = 'player1' if winner == 'X' else 'player2' if winner == 'O' else 'draw'
                    await sync_to_async(match.save)()  # Sauvegarder les modifications

                    await self.send(text_data=json.dumps({
                        'message': f'Match finished! Winner: {match.winner}',
                        'board_state': match.board_state
                    }))
                else:
                    await sync_to_async(match.save)()  # Sauvegarder les modifications
                    await self.send(text_data=json.dumps({
                        'message': f'{player} played at position {move}',
                        'board_state': match.board_state
                    }))
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Invalid move'
                }))
        elif action == 'leave_match':
            match_id = data.get('match_id')
            username = data.get('username')

            try:
                match = await sync_to_async(Match.objects.get)(id=match_id)
            except Match.DoesNotExist:
                await self.send(text_data=json.dumps({
                    'error': 'Match not found'
                }))
                return

            # Marquer le match comme terminé
            match.is_finished = True
            match.winner = 'player2' if match.player1.username == username else 'player1'
            await sync_to_async(match.save)()

            await self.send(text_data=json.dumps({
                'message': f'{username} left the match. Winner: {match.winner}'
            }))
        else:
            # Envoie un message d'erreur si l'action est inconnue
            await self.send(text_data=json.dumps({
                'error': f'Unknown action: {action}'
            }))

def check_winner(board):
    # Définir les combinaisons gagnantes
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Lignes
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colonnes
        [0, 4, 8], [2, 4, 6]              # Diagonales
    ]

    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] != '-':
            return board[combo[0]]  # Retourne 'X' ou 'O' pour le gagnant

    if '-' not in board:
        return 'draw'  # Égalité si le plateau est plein

    return None  # Pas encore de gagnant