import requests, time, logging

class HttpClient:
    def __init__(self, retries=3, delay=1):
        self.retries = retries
        self.delay = delay
        self.session = requests.Session()

    def get(self, url, params=None, headers=None, timeout=10):
        last_exc = None
        for attempt in range(self.retries):
            try:
                logging.debug(f'GET {url} params={params}')
                r = self.session.get(url, params=params, headers=headers, timeout=timeout)
                r.raise_for_status()
                try:
                    return r.json()
                except ValueError:
                    return r.text
            except Exception as e:
                last_exc = e
                logging.warning(f'Request error ({attempt+1}/{self.retries}) to {url}: {e}')
                time.sleep(self.delay)
        raise last_exc
