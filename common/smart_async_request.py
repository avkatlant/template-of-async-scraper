from dataclasses import dataclass
from typing import Any

import aiohttp

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Referer": "https://www.google.com/",
}


@dataclass
class SmartResponse:
    url: str
    status_code: int | None = None
    content: bytes | None = None
    error: str | None = None


class SmartAsyncRequest:
    """Async request implementation with custom settings."""

    def __init__(self, retry: int = 1, timeout: int = 6, headers: dict[str, Any] = HEADERS) -> None:
        self.retry = retry
        self.timeout = timeout
        self.headers = headers

    async def request(
        self,
        url: str,
        method: str = "GET",
        proxy: str | None = None,
        timeout: int = 6,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        allow_redirects: bool = True,
        retry: int | None = None,
    ) -> SmartResponse:
        response = SmartResponse(url=url)

        for _ in range(retry or self.retry):
            resp = await self._request(
                url=url,
                method=method,
                proxy=proxy,
                timeout=timeout or self.timeout,
                headers=headers or self.headers,
                data=data,
                allow_redirects=allow_redirects,
            )
            response = resp
            if resp.status_code == 200:
                break
        return response

    async def _request(
        self,
        url: str,
        method: str = "GET",
        proxy: str | None = None,
        timeout: int = 6,
        headers: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        allow_redirects: bool = True,
    ) -> SmartResponse:
        response = SmartResponse(url=url)

        if proxy:
            proxy = f"http://{proxy}"

        try:
            async with aiohttp.ClientSession(headers=self.headers) as self._session:
                async with self._session.request(
                    method=method,
                    url=url,
                    proxy=proxy,
                    timeout=timeout or self.timeout,
                    headers=headers or self.headers,
                    data=data,
                    allow_redirects=allow_redirects,
                ) as resp:
                    response.status_code = resp.status
                    response.content = await resp.read()

        except Exception as e:
            response.error = f"{type(e)} - {str(e)}"

        return response

    async def __call__(self, *args: Any, **kwargs: Any) -> SmartResponse:
        return await self.request(*args, **kwargs)
