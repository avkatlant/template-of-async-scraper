import time
from datetime import timedelta

from common.utils import get_date_time_now
from proxy.facade import Facade
from settings import MAX_CUSTOM_WORKER, MAX_WORKERS_PROXIES, URL_FOR_SECOND_CHECK

if __name__ == "__main__":
    start_data_time = get_date_time_now()
    start_time = time.monotonic()

    facad = Facade(
        url_of_second_check=URL_FOR_SECOND_CHECK,
        max_workers_proxies=MAX_WORKERS_PROXIES,
        max_custom_worker=MAX_CUSTOM_WORKER,
    )
    facad.run()

    time_work = time.monotonic() - start_time
    print(f"\nStart time: {start_data_time}")
    print(f"Working time: {time_work:.2f} sec / {timedelta(seconds=time_work)}")
