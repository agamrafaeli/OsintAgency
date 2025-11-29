from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Any
import os

class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def persist_messages(
        self,
        channel_id: str,
        messages: Iterable[Mapping[str, object]],
    ) -> int:
        """Upsert message records into the storage."""
        pass

    @abstractmethod
    def fetch_messages(
        self,
        channel_id: str | None = None,
    ) -> list[dict[str, object]]:
        """Return stored messages ordered by message id."""
        pass

    @abstractmethod
    def persist_detected_verses(
        self,
        detected_verses: Iterable[Mapping[str, object]],
        *,
        message_ids: Iterable[int | str] | None = None,
    ) -> int:
        """Upsert detected verse rows independently from message storage."""
        pass

    @abstractmethod
    def persist_forwarded_channels(
        self,
        forwarded_channels: Iterable[Mapping[str, object]],
        *,
        message_ids: Iterable[int | str] | None = None,
    ) -> int:
        """Upsert forwarded channel references independently from message storage."""
        pass
