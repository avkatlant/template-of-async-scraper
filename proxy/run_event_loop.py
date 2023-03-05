import asyncio

from .checker import CheckerProxy
from .providers import Provider


class RunEventLoop:
    """
    This class implements an infinite run event loop.
    """

    def __init__(
        self,
        max_workers_proxies: int,
        providers_list: list[Provider],
        checker_proxy: CheckerProxy,
        max_custom_worker: int,
    ) -> None:
        self._running: bool = True
        self._locker = asyncio.Lock()

        self._unchecked_proxies_queue: asyncio.Queue[str] = asyncio.Queue()
        self._unchecked_proxies_list: list[str] = []
        self._checked_proxies_list: list[str] = []
        self._checked_proxies_temp: list[str] = []
        self._count_of_completed_proxy_checks = 0

        self.max_workers_proxies = max_workers_proxies
        self.max_custom_worker = max_custom_worker
        self.providers_list = providers_list
        self.checker_proxy = checker_proxy

        self.condition_get_un_prx = asyncio.Condition()
        self.condition_create_un_prx_qu = asyncio.Condition()

    def terminate(self) -> None:
        """Terminate cycles in threads."""
        self._running = False

    def report(self) -> None:
        """Report of the number of proxies processed."""
        print(f"\n{len(self._unchecked_proxies_list)=}")
        print(f"{self._unchecked_proxies_queue.qsize()=}")
        print(f"{self._count_of_completed_proxy_checks=}")
        print(f"{len(self._checked_proxies_list)=}")
        print(f"{len(self._checked_proxies_temp)=}\n")

    async def getting_reports(self, time_sleep: int = 0) -> None:
        """Getting reports inside the threads."""
        while self._running:
            self.report()
            await asyncio.sleep(time_sleep)

    async def get_unchecked_proxies(self) -> None:
        """Getting unchecked proxies."""
        while self._running:
            async with self.condition_get_un_prx:
                await self.condition_get_un_prx.wait()
                results_providers: list[str] = await asyncio.gather(
                    *[provider() for provider in self.providers_list],
                    return_exceptions=True,
                )
                async with self._locker:
                    for result_provider in results_providers:
                        self._unchecked_proxies_list.extend(result_provider)

                async with self.condition_create_un_prx_qu:
                    self.condition_create_un_prx_qu.notify_all()

    async def create_unchecked_proxies_queue(self) -> None:
        """Create a queue of unchecked proxies."""
        while self._running:
            async with self.condition_create_un_prx_qu:
                await self.condition_create_un_prx_qu.wait()
                for proxy in self._unchecked_proxies_list:
                    await self._unchecked_proxies_queue.put(proxy)

    async def get_checked_proxies(self) -> None:
        """Getting checked proxies."""
        while self._running:
            if self._unchecked_proxies_queue.qsize() == 0:
                await asyncio.sleep(1)
            else:
                proxy: str = await self._unchecked_proxies_queue.get()
                is_good_proxy = await self.checker_proxy(proxy)
                async with self._locker:
                    if is_good_proxy:
                        print(f"GOOD PROXY: {proxy}")
                        self._checked_proxies_temp.append(proxy)
                    self._count_of_completed_proxy_checks += 1

    async def watcher(self) -> None:
        """Watcher of proxies check."""
        while self._running:
            await asyncio.sleep(1)

            if self._count_of_completed_proxy_checks == len(self._unchecked_proxies_list):
                self._count_of_completed_proxy_checks = 0
                self._unchecked_proxies_list.clear()

                if len(self._checked_proxies_temp) != 0:
                    self._checked_proxies_list = [*self._checked_proxies_temp]
                self._checked_proxies_temp.clear()

                async with self.condition_get_un_prx:
                    self.condition_get_un_prx.notify_all()

    async def custom_worker(self) -> None:
        while self._running:
            if len(self._checked_proxies_list) == 0:
                await asyncio.sleep(1)
            else:
                # Custom Code
                pass

    async def main(self) -> None:
        await asyncio.gather(
            self.get_unchecked_proxies(),
            self.create_unchecked_proxies_queue(),
            *[self.get_checked_proxies() for _ in range(self.max_workers_proxies)],
            *[self.custom_worker() for _ in range(self.max_custom_worker)],
            self.watcher(),
            self.getting_reports(1),
            return_exceptions=True,
        )

    def run(self) -> None:
        try:
            asyncio.run(self.main())

        except KeyboardInterrupt:
            self._running = False

        finally:
            print("Finish")
