import requests
import time
import logging

class HttpClient:
    def __init__(self, retries=3, delay=2):
        self.retries = retries
        self.delay = delay
        self.session = requests.Session()

    def get_json(self, url, params=None, headers=None, timeout=10):
        for attempt in range(self.retries):
            try:
                logging.debug(f"GET {url} params={params}")
                r = self.session.get(url, params=params, headers=headers, timeout=timeout)
                r.raise_for_status()
                try:
                    return r.json()
                except ValueError:
                    return r.text
            except Exception as e:
                logging.warning(f"Request failed ({attempt+1}/{self.retries}) to {url}: {e}")
                if attempt < self.retries - 1:
                    time.sleep(self.delay)
                else:
                    raise
