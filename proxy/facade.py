from .checker import CheckerProxy
from .providers import PROVIDERS
from .run_event_loop import RunEventLoop


class Facade:
    def __init__(
        self, max_workers_proxies: int, max_custom_worker: int, url_of_second_check: str | None = None
    ) -> None:
        self.url_of_second_check = url_of_second_check
        self.max_workers_proxies = max_workers_proxies
        self.max_custom_worker = max_custom_worker

    def run(self) -> None:
        checker_proxy = CheckerProxy(url_of_second_check=self.url_of_second_check)

        rt = RunEventLoop(
            max_workers_proxies=self.max_workers_proxies,
            providers_list=PROVIDERS,
            checker_proxy=checker_proxy,
            max_custom_worker=self.max_custom_worker,
        )
        rt.run()
