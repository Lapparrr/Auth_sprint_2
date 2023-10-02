import abc
from functools import lru_cache

from yandex_oauth import yao
from yandexid import YandexOAuth, YandexID

from src.models.data import OAuthUserData
from src.settings import settings


class OAuthBase(abc.ABC):
    @abc.abstractmethod
    def get_auth_url(self) -> str:
        pass

    @abc.abstractmethod
    async def get_user_data(self, code) -> OAuthUserData:
        pass


class BaseProvider:
    providers = None

    @classmethod
    def get_provider(cls, provider_name):
        if cls.providers is None:
            cls.providers = {}
            for provider_class in cls.__subclasses__():
                provider = provider_class()
                cls.providers[provider.name] = provider
        return cls.providers.get(provider_name)


class YandexProvider(OAuthBase, BaseProvider):
    def __init__(self) -> None:
        self.name = "yandex"
        self.yandex_oauth = YandexOAuth(
            client_id=settings.yandex_client_id,
            client_secret=settings.yandex_client_secret,
            redirect_uri=settings.yandex_redirect_uri,
        )

    def get_auth_url(self):
        return self.yandex_oauth.get_authorization_url()

        pass
    async def get_user_data(self, code) -> OAuthUserData:
        tokens = yao.get_token_by_code(
            code,
            settings.yandex_client_id,
            settings.yandex_client_secret
        )
        user_data = YandexID(tokens.get('access_token')).get_user_info_json()
        return OAuthUserData(
            email=user_data.default_email,
            login=user_data.login,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            social_id=user_data.psuid,
            social_name=self.name,
        )


@lru_cache()
def yandex_provider_service(
) -> YandexProvider:
    return YandexProvider()
