import os
from typing import Optional

from osintagency.storage.interface import StorageBackend
from osintagency.storage.backends.peewee_backend import PeeweeStorage

def get_storage_backend(db_path: Optional[str] = None) -> StorageBackend:
    """
    Factory to get the configured storage backend.
    
    Args:
        db_path: Optional override for the database path.
    
    Returns:
        An instance of StorageBackend.
    """
    # Currently only PeeweeStorage is supported.
    # In the future, we could read config/env vars to decide which backend to return.
    return PeeweeStorage(db_path=db_path)
