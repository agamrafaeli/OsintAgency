"""Peewee ORM schema definitions for OsintAgency storage."""

from __future__ import annotations

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    CompositeKey,
    DatabaseProxy,
    FloatField,
    IntegerField,
    Model,
    TextField,
)

database_proxy: DatabaseProxy = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class StoredMessage(BaseModel):
    channel_id = CharField()
    message_id = IntegerField()
    posted_at = TextField(null=True)
    text = TextField()
    raw_payload = TextField()

    class Meta:
        table_name = "messages"
        primary_key = CompositeKey("channel_id", "message_id")


class DetectedVerse(BaseModel):
    id = AutoField()
    message_id = IntegerField()
    sura = IntegerField()
    ayah = IntegerField()
    confidence = FloatField()
    is_partial = BooleanField(default=False)

    class Meta:
        table_name = "detected_verses"


class Subscription(BaseModel):
    channel_id = CharField(primary_key=True)
    name = TextField(null=True)
    added_at = TextField()
    active = BooleanField(default=True)
    metadata = TextField(null=True)

    class Meta:
        table_name = "subscriptions"


__all__ = [
    "database_proxy",
    "BaseModel",
    "StoredMessage",
    "DetectedVerse",
    "Subscription",
]
