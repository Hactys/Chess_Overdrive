

class WSManager:
    def __init__(self):
        self.active = set()

    def connect(self, ws):
        self.active.add(ws)

    def disconnect(self, ws):
        self.active.remove(ws)

    async def broadcast(self, message: str):
        for ws in list(self.active):
            try:
                await ws.send_text(message)
            except Exception as e:
                print(f"error in ws_manager : '{e}'")
                self.disconnect(ws)

ws_manager = WSManager()
