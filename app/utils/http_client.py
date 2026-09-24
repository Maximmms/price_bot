"""Общий асинхронный HTTP-клиент на базе aiohttp."""

import aiohttp


class HTTPClient:
    """Асинхронный HTTP-клиент с общим session."""

    _session: aiohttp.ClientSession | None = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        """Получить или создать общий session."""
        if cls._session is None or cls._session.closed:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        """Закрыть общий session."""
        if cls._session and not cls._session.closed:
            await cls._session.close()

    @classmethod
    async def get(cls, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Выполнить GET запрос."""
        session = await cls.get_session()
        response = await session.get(url, **kwargs)
        response.raise_for_status()
        return response

    @classmethod
    async def post(cls, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Выполнить POST запрос."""
        session = await cls.get_session()
        response = await session.post(url, **kwargs)
        response.raise_for_status()
        return response

    @classmethod
    async def get_json(cls, url: str, **kwargs) -> dict:
        """Выполнить GET запрос и вернуть JSON."""
        response = await cls.get(url, **kwargs)
        return await response.json()
