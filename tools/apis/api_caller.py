import logging
from typing import Dict, Callable

import requests


class APICaller:

    def __init__(self, base_api_url: str, headers: Dict[str, str] = None):
        self.base_api_url = base_api_url
        self.headers = headers

    def retry_on_timeouts(self, function_to_retry: Callable, response_timeout: float = 5.0, max_retries: int = 3,
                          **kwargs) -> requests.Response:
        for attempt in range(max_retries):
            try:
                response = function_to_retry(response_timeout=response_timeout, **kwargs)
            except requests.exceptions.Timeout:
                logging.warning(f"Retrying a timed out call to base-url --> {self.base_api_url}{kwargs['url_extension']}")
                response_timeout *= 2
                continue
            else:
                break
        else:
            raise requests.exceptions.Timeout

        return response

    def make_get_request(self, url_extension: str, response_timeout: float = 5.0,
                         max_retries: int = 3) -> requests.Response:
        try:
            return self.retry_on_timeouts(self.make_raw_get_request,
                                          response_timeout,
                                          max_retries,
                                          url_extension=url_extension)
        except requests.exceptions.Timeout as e:
            logging.exception(f"Timeout max. retries of {max_retries} exceeded unsuccessfully")
            raise e
        except requests.exceptions.RequestException as e:
            logging.exception(f"Call to {self.base_api_url}{url_extension} failed --> {e}")
            raise e

    def make_post_request(self, url_extension: str, response_timeout: float = 5.0, max_retries: int = 3,
                          payload: Dict = None) -> requests.Response:

        return self.retry_on_timeouts(self.make_raw_post_request,
                                      response_timeout,
                                      max_retries,
                                      url_extension=url_extension,
                                      payload=payload)

    def make_raw_get_request(self, url_extension: str, response_timeout: float = 5.0) -> requests.Response:

        response = requests.get(url=f"{self.base_api_url}{url_extension}",
                                headers=self.headers,
                                timeout=response_timeout)

        return response

    def make_raw_post_request(self, url_extension: str, response_timeout: float = 5.0,
                              payload: Dict = None) -> requests.Response:

        response = requests.post(url=f"{self.base_api_url}{url_extension}",
                                 data=payload,
                                 headers=self.headers,
                                 timeout=response_timeout)

        return response
