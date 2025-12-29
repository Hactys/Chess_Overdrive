from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, emit

from game_engine.server.game_manager import GameManager
from game_engine.server.schemas import state_to_dict
from game_engine.server.api_actions import parse_action


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

manager = GameManager()


# API HTTP 
@app.route("/create", methods=["POST"])
def create_game():
    data = request.json
    game_id = data["game_id"]
    players = data["players"]  # {"white": {...}, "black": {...}}

    game = manager.create_game(game_id, players)
    return jsonify({"status": "ok", "game_id": game_id})


# WebSocket 
@socketio.on("join")
def join_game(data):
    game_id = data["game_id"]
    player_id = data["player"]

    join_room(game_id)

    game = manager.get_game(game_id)
    emit("state", state_to_dict(game.state), room=game_id)  # type: ignore


@socketio.on("action")
def handle_action(data):
    print(f"In action, data : {data}")
    game_id = data["game_id"]
    game = manager.get_game(game_id)

    action = parse_action(data["action"])

    if game.apply_action(action):
        socketio.emit("state", state_to_dict(game.state), room=game_id)  # type: ignore
    else:
        socketio.emit("error", {"msg": "Invalid action"}, room=request.sid)  # type: ignore


@socketio.on("get_legal_moves")
def ws_legal_moves(data):
    game_id = data["game_id"]
    pos = data["from"]
    player = data.get("player", "white")

    game = manager.get_game(game_id)
    moves = game.get_legal_moves(player, pos)

    emit("legal_moves_result", {"from": pos, "moves": moves}, room=game_id)  # type: ignore


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
