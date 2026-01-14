from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room

from game_engine.rules.combat import calculate_combat_proba
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
    players = data["players"]  # {"uuid-1": {...}, "uuid-2": {...}}

    game = manager.create_game(game_id, players)
    return jsonify({"status": "ok", "game_id": game_id})


@app.route("/join", methods=["POST"])
def join_game():
    data = request.json
    if not data:
        return jsonify({"error": "missing json body"}), 400
    game_id = data.get("game_id")
    player = data.get("player")

    if not game_id or not player:
        return jsonify({"error": "invalid payload"}), 400
    player_id = player.get("player_id")
    username = player.get("username")
    if not player_id:
        return jsonify({"error": "missing player_id"}), 400
    game = manager.games.get(game_id)
    if not game:
        return jsonify({"error": "game not found"}), 404
    ok = game.add_player(player_id, username)
    if not ok:
        return jsonify({"error": "game already has two players"}), 400
    return jsonify({"status": "ok"})


# WebSocket
@socketio.on("join")
def ws_join_game(data):
    game_id = data["game_id"]
    player_id = data["player"]

    join_room(game_id)

    game = manager.get_game(game_id)
    socketio.emit("state", state_to_dict(game.state), room=game_id)  # type: ignore


@socketio.on("action")
def ws_handle_action(data):
    game_id = data["game_id"]
    game = manager.get_game(game_id)
    player_id = data.get("player_id")
    if not player_id:
        socketio.emit("error", {"msg": "Missing player_id"}, room=request.sid)  # type: ignore
        return

    action = parse_action({**data["action"], "player_id": player_id})

    if game.apply_action(action):
        socketio.emit("state", state_to_dict(game.state), room=game_id)  # type: ignore
    else:
        socketio.emit("error", {"msg": "Invalid action"}, room=request.sid)  # type: ignore


@socketio.on("get_legal_moves")
def ws_legal_moves(data: dict):
    game_id = data["game_id"]
    pos = data["from"]
    player_id = data.get("player", None)

    if player_id is None:
        socketio.emit("error", {"msg": "Missing player_id"}, room=request.sid)  # type: ignore
        return

    game = manager.get_game(game_id)
    board = game.state.board

    if player_id not in game.state.players.keys():
        socketio.emit("error", {"msg": "Not a player"}, room=request.sid)  # type: ignore
        return
    if player_id not in game.state.players:
        socketio.emit("error", {"msg": "Not a player in this game"}, room=request.sid)  # type: ignore
        return
    if player_id != game.state.current_player:
        socketio.emit("legal_moves", [], room=request.sid)  # type: ignore
        return

    attacker = board.get_piece(pos)
    if attacker is None:
        return

    moves = game.get_legal_moves(player_id, pos)
    capture_probas = {}

    for pos in moves:
        defender = board.get_piece(pos)
        if defender and defender.owner != attacker.owner:
            proba = calculate_combat_proba(game, attacker, defender)
            capture_probas[pos] = proba

    socketio.emit(
        "legal_moves_result",
        {"game_id": game_id, "from": pos, "moves": moves, "capture_probas": capture_probas},
        room=game_id,  # type: ignore
    )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
