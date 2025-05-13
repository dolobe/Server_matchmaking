from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import websocket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# WebSocket client to communicate with the server
server_ws = None

def connect_to_server():
    global server_ws
    server_ws = websocket.WebSocketApp(
        "ws://127.0.0.1:8000/ws/matchmaking/",
        on_message=on_server_message,
        on_error=on_server_error,
        on_close=on_server_close
    )
    server_ws.run_forever()

def on_server_message(ws, message):
    data = json.loads(message)
    print(f"Message from server: {data}")
    socketio.emit('server_message', data)

def on_server_error(ws, error):
    print(f"WebSocket error: {error}")

def on_server_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/queue', methods=['POST'])
def join_queue():
    username = request.json.get('username')
    if username:
        server_ws.send(json.dumps({"action": "join_queue", "username": username}))
        return jsonify({'status': 'success', 'message': 'Joined queue'})
    return jsonify({'status': 'error', 'message': 'Username is required'})

@app.route('/game')
def game():
    return render_template('game.html')

@socketio.on('play_turn')
def play_turn(data):
    match_id = data.get('match_id')
    player = data.get('player')
    move = data.get('move')
    server_ws.send(json.dumps({
        "action": "play_turn",
        "match_id": match_id,
        "player": player,
        "move": move
    }))

if __name__ == "__main__":
    import threading
    threading.Thread(target=connect_to_server).start()
    socketio.run(app, debug=True)