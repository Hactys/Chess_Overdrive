import socketio, requests


SERVER_URL = "http://localhost:5000"
WS_URL = "http://localhost:5000"
GAME_ID = "test_game"
PLAYER = "white"
sio_connected = False

sio = socketio.Client()

lock = threading.Lock()

latest_state = None
new_state_available = False
legal_moves_cache = None
new_legal_moves = False


def init_network(app):
    """Démarre la connexion serveur + crée la partie par défaut"""
    global sio_connected
    if sio_connected:
        print("[WS] Socket.IO already connected, skipping connection")
        return
    try:
        requests.post(f"{SERVER_URL}/create", json={
            "game_id": GAME_ID,
            "players": {"white": {}, "black": {}}
        })
        print("[API] Game created")
    except:
        print(traceback.format_exc())
        print("[API] Engine unreachable")

    @sio.event
    def connect():
        sio.emit("join", {"game_id": GAME_ID, "player": PLAYER})
        print("[WS] Connected")

    @sio.on("state")  # type: ignore
    def receive_state(data):
        global latest_state, new_state_available
        with lock:
            latest_state = data
            new_state_available = True

    @sio.on("legal_moves_result")  # type: ignore
    def on_legal_moves(data):
        global legal_moves_cache, new_legal_moves
        with lock:
            legal_moves_cache = data["moves"]
            new_legal_moves = True

    sio.connect(WS_URL, transports=["websocket", "polling"], namespaces=["/"])
    sio_connected = True


def pull_state():
    """Appelé en polling pour mise à jour Dash"""
    global new_state_available
    with lock:
        if new_state_available and latest_state:
            new_state_available = False
            return latest_state
        return None

def pull_moves():
    """Appelé en polling pour mise à jour Dash"""
    global new_legal_moves
    with lock:
        if new_legal_moves and legal_moves_cache is not None:
            new_legal_moves = False
            return legal_moves_cache
        return None
