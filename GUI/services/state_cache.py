import asyncio

_state = None  # TODO : remplacer tout ça par des dict pour la version multijoueur
_moves = None
_probas = None
_selected = None

_lock = asyncio.Lock()


async def set_state(state):
    global _state
    async with _lock:
        _state = state

async def get_state():
    async with _lock:
        return _state


async def set_moves(moves, probas):
    global _moves, _probas
    async with _lock:
        _moves = moves
        _probas = probas

async def get_moves():
    async with _lock:
        return _moves, _probas
    
async def clear_moves():
    global _moves, _probas
    async with _lock:
        _moves = None
        _probas = None


async def set_selected(pos: str | None):
    global _selected
    async with _lock:
        _selected = pos

async def get_selected():
    async with _lock:
        return _selected