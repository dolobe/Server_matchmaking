import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import User, Queue, Match, Turn

active_players = {}

class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.user = None
        self.match = None

    async def disconnect(self, close_code):
        if self.user:
            await self.remove_from_queue(self.user.username)
            if self.user.username in active_players:
                del active_players[self.user.username]

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "join_queue":
            username = data.get("username")
            self.user = await self.get_or_create_user(username)
            active_players[self.user.username] = self.channel_name
            await self.add_to_queue(self.user)
            await self.try_matchmaking()

        elif action == "play_move":
            x, y = data.get("x"), data.get("y")
            await self.handle_move(x, y)

        elif action == "end_match":
            result = data.get("result")
            await self.handle_end_match(result)

    @database_sync_to_async
    def get_or_create_user(self, username):
        user, _ = User.objects.get_or_create(username=username)
        return user

    @database_sync_to_async
    def add_to_queue(self, user):
        if not Queue.objects.filter(user=user).exists():
            Queue.objects.create(user=user)

    @database_sync_to_async
    def remove_from_queue(self, username):
        try:
            user = User.objects.get(username=username)
            Queue.objects.filter(user=user).delete()
        except User.DoesNotExist:
            pass

    @database_sync_to_async
    def get_two_users_from_queue(self):
        queues = list(Queue.objects.select_related('user').all()[:2])
        if len(queues) < 2:
            return None, None
        user1 = queues[0].user
        user2 = queues[1].user
        queues[0].delete()
        queues[1].delete()
        return user1.username, user2.username

    async def try_matchmaking(self):
        user1_name, user2_name = await self.get_two_users_from_queue()
        if user1_name and user2_name:
            user1 = await database_sync_to_async(User.objects.get)(username=user1_name)
            user2 = await database_sync_to_async(User.objects.get)(username=user2_name)
            match = await database_sync_to_async(Match.objects.create)(
                player1=user1, player2=user2, board_state=" " * 9
            )

            await self.channel_layer.group_add(f"match_{match.id}", active_players[user1.username])
            await self.channel_layer.group_add(f"match_{match.id}", active_players[user2.username])

            await self.channel_layer.send(
                active_players[user1.username],
                {
                    "type": "start.match",
                    "opponent": user2.username,
                    "symbol": "X",
                    "match_id": match.id,
                    "your_turn": True
                }
            )
            await self.channel_layer.send(
                active_players[user2.username],
                {
                    "type": "start.match",
                    "opponent": user1.username,
                    "symbol": "O",
                    "match_id": match.id,
                    "your_turn": False
                }
            )

    async def start_match(self, event):
        await self.send(text_data=json.dumps({
            "action": "start_match",
            "opponent": event["opponent"],
            "symbol": event["symbol"],
            "match_id": event["match_id"],
            "your_turn": event["your_turn"]
        }))
        self.match_id = event["match_id"]
        self.symbol = event["symbol"]

    async def handle_move(self, x, y):
        match = await database_sync_to_async(Match.objects.get)(id=self.match_id)
        board = list(match.board_state)
        idx = x * 3 + y
        if board[idx] != " ":
            return
        board[idx] = self.symbol
        new_state = "".join(board)

        await self.save_move(match, self.user, x, y, new_state)

        winner = self.check_winner(board)
        is_draw = " " not in board

        if winner:
            await self.finish_match(match, self.user)
            await self.channel_layer.group_send(
                f"match_{self.match_id}",
                {
                    "type": "end.match",
                    "winner": self.user.username
                }
            )
        elif is_draw:
            await self.finish_match(match, None)
            await self.channel_layer.group_send(
                f"match_{self.match_id}",
                {
                    "type": "end.match",
                    "winner": "draw"
                }
            )
        else:
            await self.channel_layer.group_send(
                f"match_{self.match_id}",
                {
                    "type": "opponent.move",
                    "x": x,
                    "y": y,
                    "symbol": self.symbol
                }
            )

    @database_sync_to_async
    def save_move(self, match, user, x, y, new_state):
        match.board_state = new_state
        match.save()
        Turn.objects.create(match=match, player=user, move=f"{x},{y}")

    @database_sync_to_async
    def finish_match(self, match, winner_user):
        match.is_finished = True
        match.winner = winner_user.username if winner_user else "draw"
        match.save()

    def check_winner(self, board):
        wins = [
            [0,1,2], [3,4,5], [6,7,8],
            [0,3,6], [1,4,7], [2,5,8],
            [0,4,8], [2,4,6]
        ]
        for a, b, c in wins:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return True
        return False

    async def opponent_move(self, event):
        await self.send(text_data=json.dumps({
            "action": "opponent_move",
            "x": event["x"],
            "y": event["y"],
            "symbol": event["symbol"]
        }))

    async def end_match(self, event):
        await self.send(text_data=json.dumps({
            "action": "end_match",
            "winner": event["winner"]
        }))
