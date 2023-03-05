from common.smart_async_request import SmartAsyncRequest

JUDGES_LIST = [
    "http://httpbin.org/get?show_env",
    "http://www.proxy-listen.de/azenv.php",
    "https://www2.htw-dresden.de/~beck/cgi-bin/env.cgi",
    "http://www.meow.org.uk/cgi-bin/env.pl",
    "http://www.wfuchs.de/azenv.php",
    "http://wfuchs.de/azenv.php",
    "https://users.ugent.be/~bfdwever/start/env.cgi",
    "http://www.suave.net/~dave/cgi/env.cgi",
    "http://www.cknuckles.com/cgi/env.cgi",
    "http://httpheader.net",
    "http://kheper.csoft.net/stuff/env.cgi",
    "http://proxyjudge.us",
    "http://www.proxyjudge.biz",
    "http://azenv.net",
    "http://coincompare.ml/",
    "https://www.andrews.edu/~bidwell/examples/env.cgi",
    "http://shinh.org/env.cgi",
    "http://users.on.net/~emerson/env/env.pl",
    "http://www.9ravens.com/env.cgi",
    "http://www2t.biglobe.ne.jp/~take52/test/env.cgi",
    "http://www3.wind.ne.jp/hassii/env.cgi",
    "http://xrea.fukuyan.net/env.cgi",
]


class CheckerProxy:
    """Checking the proxy for life.

    url_of_second_check (str | None): Additional verification on a specific site. Defaults to None.
    """

    def __init__(self, url_of_second_check: str | None = None) -> None:
        self._request = SmartAsyncRequest()
        self.judges = JUDGES_LIST
        self.url_of_second_check = url_of_second_check

    async def checker(self, proxy: str) -> bool:
        try:
            for judge in self.judges:
                resp = await self._request(url=judge, proxy=proxy, timeout=3, allow_redirects=False)

                if resp.status_code == 200:
                    if not self.url_of_second_check:
                        return True

                    resp_second_check = await self._request(
                        url=self.url_of_second_check, proxy=proxy, timeout=6, allow_redirects=False
                    )
                    if resp_second_check.status_code == 200:
                        return True

        except Exception:
            pass

        return False

    async def __call__(self, proxy: str) -> bool:
        return await self.checker(proxy)
