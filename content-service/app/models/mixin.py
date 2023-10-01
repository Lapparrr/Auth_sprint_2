from uuid import UUID

import orjson

# Используем pydantic для упрощения работы при перегонке данных
# из json в объекты
from pydantic import BaseModel


def orjson_dumps(data, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode,
    # поэтому декодируем
    return orjson.dumps(data, default=default).decode()


class MixinModel(BaseModel):
    """Базовая модель."""

    uuid: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
