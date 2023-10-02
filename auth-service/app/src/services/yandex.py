from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from yandex_oauth import yao

from src.db.postgres import get_session
from src.models.data import YandexUserData
from src.settings import settings

from yandexid import YandexOAuth, YandexID


class YandexProvider:
    def __init__(self, pg: AsyncSession) -> None:
        self.name = "yandex"
        self.yandex_oauth = YandexOAuth(
            client_id=settings.yandex_client_id,
            client_secret=settings.yandex_client_secret,
            redirect_uri=settings.yandex_redirect_uri,
        )
        self.pg = pg

    def get_auth_url(self):
        return self.yandex_oauth.get_authorization_url()

    async def get_user_data(self, code) -> YandexUserData:
        tokens = yao.get_token_by_code(
            code,
            settings.yandex_client_id,
            settings.yandex_client_secret
        )
        user_data = YandexID(tokens.get('access_token')).get_user_info_json()
        return YandexUserData.parse_obj(user_data)


@lru_cache()
def yandex_provider_service(
    pg: AsyncSession = Depends(get_session),
) -> YandexProvider:
    return YandexProvider(
        pg=pg,
    )
