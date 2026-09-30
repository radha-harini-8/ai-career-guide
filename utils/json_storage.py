import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def ensure_parent_dir(file_path: str | os.PathLike) -> None:
    """Create the folder for a JSON file if it does not exist."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    """Return ISO-8601 timestamp in UTC."""
    return datetime.now(timezone.utc).isoformat()


def load_json(file_path: str | os.PathLike, default=None):
    """Load a JSON file, creating it with a default value if it is missing."""
    file_path = Path(file_path)
    ensure_parent_dir(file_path)

    if not file_path.exists():
        default_value = [] if default is None else default
        save_json(file_path, default_value)
        return default_value

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data if data is not None else (default if default is not None else [])
    except (json.JSONDecodeError, OSError):
        fallback = [] if default is None else default
        save_json(file_path, fallback)
        return fallback


def save_json(file_path: str | os.PathLike, payload: Any) -> None:
    """Write a JSON object to disk."""
    file_path = Path(file_path)
    ensure_parent_dir(file_path)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)


def add_record(file_path: str | os.PathLike, record: Dict[str, Any], record_id_key: str = 'id') -> Dict[str, Any]:
    """Append a record to a JSON list and ensure it includes timestamps and id."""
    storage = load_json(file_path, [])
    if not isinstance(storage, list):
        storage = []

    record.setdefault(record_id_key, f"record_{len(storage) + 1}")
    record.setdefault('created_at', utc_now_iso())
    record['updated_at'] = utc_now_iso()

    storage.append(record)
    save_json(file_path, storage)
    return record


def update_record(file_path: str | os.PathLike, record_id: str, updated_fields: Dict[str, Any], record_id_key: str = 'id') -> Dict[str, Any] | None:
    """Update a record by id in a JSON list file."""
    storage = load_json(file_path, [])
    if not isinstance(storage, list):
        return None

    for index, record in enumerate(storage):
        if record.get(record_id_key) == record_id:
            record.update(updated_fields)
            record['updated_at'] = utc_now_iso()
            storage[index] = record
            save_json(file_path, storage)
            return record
    return None


def get_record(file_path: str | os.PathLike, record_id: str, record_id_key: str = 'id') -> Dict[str, Any] | None:
    """Return a record by id."""
    storage = load_json(file_path, [])
    if not isinstance(storage, list):
        return None

    for record in storage:
        if record.get(record_id_key) == record_id:
            return record
    return None


def get_all_records(file_path: str | os.PathLike) -> List[Dict[str, Any]]:
    """Return all records from a JSON list file."""
    storage = load_json(file_path, [])
    if isinstance(storage, list):
        return storage
    return []
