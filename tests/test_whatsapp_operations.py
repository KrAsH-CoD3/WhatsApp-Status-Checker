"""
Tests for WhatsAppOperations status fetching — specifically the global fallback
that engages when the per-contact status fetch fails.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


TARGET = "1234567890@c.us"
OTHER = "9999999999@c.us"


def _status(author: str, msg_id: str, viewed: bool = False) -> dict:
    """One entry in the shape produced by patches.patched_status_get."""
    return {
        "id_serialized": f"false_{author}_{msg_id}",
        "id_id": msg_id,
        "id_participant": author,
        "id_remote": "status@broadcast",
        "isViewed": viewed,
        "author": author,
        "t": 1700000000,
        "mediaType": "image",
        "mimeType": "image/jpeg",
    }


def _ops(store_contents):
    """An WhatsAppOperations whose per-contact fetch fails and whose
    store-wide query returns `store_contents`."""
    from whatsapp_status_checker.core.whatsapp_operations import WhatsAppOperations

    bridge = MagicMock()
    bridge.conn_is_main_ready = AsyncMock(return_value=True)
    # A bridge-ish error so the fallback branch engages.
    bridge.status_get = AsyncMock(side_effect=Exception("bridge timeout"))
    bridge.status_get_all = AsyncMock(return_value=store_contents)

    wapi = MagicMock()
    wapi.bridge = bridge
    return WhatsAppOperations(wapi=wapi, media_controller=None), bridge


class TestGlobalFallback:
    """The recovery path used when status_get() cannot reach the contact."""

    @pytest.mark.asyncio
    async def test_returns_only_the_monitored_contacts_unviewed_statuses(self):
        """Must pick out the target's unviewed statuses and ignore the rest.

        The payload keys are id_remote ('status@broadcast') and author — the
        old filter looked for a nested id.remote and a 'from' key that the
        patched status_get never emits, so it always matched nothing.
        """
        ops, _ = _ops([
            _status(TARGET, "A"),
            _status(OTHER, "B"),
            _status(TARGET, "C", viewed=True),
        ])

        result = await ops.get_unviewed_statuses(TARGET, name="TestContact")

        assert [s["id_id"] for s in result] == ["A"]

    @pytest.mark.asyncio
    async def test_enumerates_the_store_instead_of_a_broadcast_wid(self):
        """status_get() is keyed by the poster's wid, so 'status@broadcast' is
        never a store key and returns nothing. The fallback must not use it."""
        ops, bridge = _ops([_status(TARGET, "A")])

        await ops.get_unviewed_statuses(TARGET, name="TestContact")

        bridge.status_get_all.assert_awaited()
        for call in bridge.status_get.await_args_list:
            assert call.args[0] != "status@broadcast"

    @pytest.mark.asyncio
    async def test_matches_on_id_participant_when_author_is_empty(self):
        """Some models only expose the key's participant, not the author."""
        entry = _status(TARGET, "A")
        entry["author"] = ""
        ops, _ = _ops([entry])

        result = await ops.get_unviewed_statuses(TARGET, name="TestContact")

        assert [s["id_id"] for s in result] == ["A"]

    @pytest.mark.asyncio
    async def test_returns_empty_when_the_contact_has_no_status(self):
        ops, _ = _ops([_status(OTHER, "B")])

        result = await ops.get_unviewed_statuses(TARGET, name="TestContact")

        assert result == []
