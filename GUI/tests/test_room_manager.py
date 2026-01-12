import pytest
from GUI.services.room_manager import RoomManager


class FakeWebSocket:
    def __init__(self):
        self.messages = []

    async def send_text(self, msg):
        self.messages.append(msg)


@pytest.mark.asyncio
async def test_room_broadcast():
    rm = RoomManager()
    ws1 = FakeWebSocket()
    ws2 = FakeWebSocket()

    rm.join("g1", ws1)
    rm.join("g1", ws2)

    await rm.broadcast("g1", "update_state")

    assert ws1.messages == ["update_state"]
    assert ws2.messages == ["update_state"]
