import json
import os
import threading
from typing import Any, Dict, List, Union


_lock_by_path: Dict[str, threading.Lock] = {}


def _get_lock(file_path: str) -> threading.Lock:
    if file_path not in _lock_by_path:
        _lock_by_path[file_path] = threading.Lock()
    return _lock_by_path[file_path]


def ensure_parent_dir(file_path: str) -> None:
    parent = os.path.dirname(file_path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def read_json(file_path: str, default: Union[Dict[str, Any], List[Any]]) -> Union[Dict[str, Any], List[Any]]:
    lock = _get_lock(file_path)
    with lock:
        if not os.path.exists(file_path):
            ensure_parent_dir(file_path)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
            return default
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
            return default


def write_json(file_path: str, data: Union[Dict[str, Any], List[Any]]) -> None:
    lock = _get_lock(file_path)
    with lock:
        ensure_parent_dir(file_path)
        tmp_path = f"{file_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, file_path)


