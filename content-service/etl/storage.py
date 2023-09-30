import abc
import json
import os
from datetime import datetime
from typing import Any, Optional


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path if file_path else "storage.json"
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump({}, f)
        self.default_val = datetime(2000, 1, 1)

    def save_state(self, state: dict) -> None:
        if os.path.exists(self.file_path):
            with open(self.file_path) as f:
                state_ = json.load(f)
        else:
            state_ = {}
        for k, v in state.items():
            state_[k] = v
        with open(self.file_path, "w") as f:
            json.dump(state_, f, default=str)

    def retrieve_state(self, key: str):
        with open(self.file_path) as f:
            state = json.load(f)
        return state.get(key, self.default_val)
