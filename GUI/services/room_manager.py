from collections import defaultdict


class RoomManager:
    def __init__(self):
        # game_id -> set(WebSocket)
        self.rooms = defaultdict(set)

    def join(self, game_id: str, ws):
        self.rooms[game_id].add(ws)

    def leave(self, game_id: str, ws):
        if ws in self.rooms.get(game_id, set()):
            self.rooms[game_id].remove(ws)
            if not self.rooms[game_id]:
                del self.rooms[game_id]

    async def broadcast(self, game_id: str, message: str):
        for ws in list(self.rooms.get(game_id, [])):
            try:
                await ws.send_text(message)
            except:
                self.leave(game_id, ws)


room_manager = RoomManager()
