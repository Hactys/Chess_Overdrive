import asyncio


_states = {}
_moves = {}
_probas = {}
_selected = {}

_lock = asyncio.Lock()


async def set_state(game_id, state):
    async with _lock:
        _states[game_id] = state

async def get_state(game_id):
    async with _lock:
        return _states.get(game_id)


async def set_moves(game_id, moves, probas):
    async with _lock:
        _moves[game_id] = moves
        _probas[game_id] = probas

async def get_moves(game_id):
    async with _lock:
        return _moves.get(game_id), _probas.get(game_id)


async def set_selected(game_id, player_id, pos):
    async with _lock:
        _selected[(game_id, player_id)] = pos

async def get_selected(game_id, player_id):
    async with _lock:
        return _selected.get((game_id, player_id))


async def clear_selected(game_id, player_id):
    async with _lock:
        _selected.pop((game_id, player_id), None)

async def clear_moves(game_id):
    async with _lock:
        _moves.pop(game_id, None)
