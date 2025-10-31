import asyncio
import datetime as dt
from types import SimpleNamespace

import pytest

from osintagency.config import TelegramConfig
from scripts import fetch_channel


class FakeTelegramClient:
    def __init__(self, session, api_id, api_hash):
        self.session = session
        self.api_id = api_id
        self.api_hash = api_hash
        self.connected = False
        self.started_with = None
        self._messages = []
        self.entities = {}

    async def connect(self):
        self.connected = True

    async def start(self, bot_token):
        self.started_with = bot_token

    async def disconnect(self):
        self.connected = False

    async def get_entity(self, channel):
        return self.entities.get(channel, channel)

    def set_messages(self, messages):
        self._messages = messages

    async def iter_messages(self, entity, limit):
        count = 0
        for message in self._messages:
            if count >= limit:
                break
            yield message
            count += 1


class FakeStringSession:
    def __init__(self, value):
        self.value = value


@pytest.mark.asyncio
async def test_create_client_uses_session(monkeypatch):
    fake_client = FakeTelegramClient(session=None, api_id=0, api_hash="")

    def fake_loader():
        def factory(session, api_id, api_hash):
            fake_client.__init__(session, api_id, api_hash)
            return fake_client

        return factory, FakeStringSession, RuntimeError

    monkeypatch.setattr(fetch_channel, "_load_telethon", fake_loader)
    config = TelegramConfig(
        api_id=123,
        api_hash="hash",
        target_channel="@channel",
        session_string="session-string",
        bot_token=None,
    )

    client = await fetch_channel._create_client(config)

    assert isinstance(client.session, FakeStringSession)
    assert client.session.value == "session-string"
    assert client.api_id == 123
    assert client.api_hash == "hash"
    assert client.connected is True
    assert client.started_with is None


@pytest.mark.asyncio
async def test_create_client_uses_bot_token(monkeypatch):
    fake_client = FakeTelegramClient(session=None, api_id=0, api_hash="")

    def fake_loader():
        def factory(session_name, api_id, api_hash):
            fake_client.__init__(session_name, api_id, api_hash)
            return fake_client

        return factory, FakeStringSession, RuntimeError

    monkeypatch.setattr(fetch_channel, "_load_telethon", fake_loader)
    config = TelegramConfig(
        api_id=123,
        api_hash="hash",
        target_channel="@channel",
        session_string=None,
        bot_token="bot-token",
    )

    client = await fetch_channel._create_client(config)

    assert client.session == "bot"
    assert client.started_with == "bot-token"
    assert client.connected is False


@pytest.mark.asyncio
async def test_fetch_messages_trims_text(monkeypatch):
    fake_client = FakeTelegramClient(session=None, api_id=0, api_hash="")
    fake_messages = [
        SimpleNamespace(id=1, date=dt.datetime(2024, 1, 1, 0, 0), message=" hello "),
        SimpleNamespace(id=2, date=None, message=None),
    ]
    fake_client.set_messages(fake_messages)

    def fake_loader():
        return lambda *args, **kwargs: fake_client, FakeStringSession, RuntimeError

    monkeypatch.setattr(fetch_channel, "_load_telethon", fake_loader)

    messages = await fetch_channel._fetch_messages(fake_client, "@channel", limit=5)

    assert messages == [
        {"id": 1, "timestamp": "2024-01-01T00:00:00", "text": "hello"},
        {"id": 2, "timestamp": None, "text": ""},
    ]

