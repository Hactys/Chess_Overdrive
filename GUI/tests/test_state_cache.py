import pytest

from GUI.services.state_cache import (
    set_state, get_state,
    set_moves, get_moves,
    set_selected, get_selected,
    clear_moves
)

@pytest.mark.asyncio
async def test_state_roundtrip():
    await set_state("g1", {"foo": "bar"})
    state = await get_state("g1")
    assert state == {"foo": "bar"}


@pytest.mark.asyncio
async def test_moves_and_probas():
    await set_moves("g1", ["a2", "a3"], {"a3": 0.7})
    moves, probas = await get_moves("g1")
    assert moves == ["a2", "a3"]
    assert probas["a3"] == 0.7


@pytest.mark.asyncio
async def test_selected_piece():
    await set_selected("g1", "white", "e2")
    sel = await get_selected("g1", "white")
    assert sel == "e2"


@pytest.mark.asyncio
async def test_clear_moves():
    await set_moves("g1", ["a2"], {})
    await clear_moves("g1")
    moves, _ = await get_moves("g1")
    assert moves is None
