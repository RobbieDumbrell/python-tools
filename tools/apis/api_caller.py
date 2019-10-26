import logging
from typing import Dict, Callable

import requests


class APICaller:

    def __init__(self, base_api_url: str, headers: Dict[str, str] = None):
        self.base_api_url = base_api_url
        self.headers = headers

    def retry_on_timeouts(self, function_to_retry: Callable, response_timeout: float = 5.0, max_retries: int = 3,
                          **kwargs) -> requests.Response:
        """
        Function to that tries and retries call to a given function a given number of times if that call returns a
        timeout error. Designed to be used with http request functions within this class, and to specify the time to wait
        for response before cancelling and trying again, to prevent hanging API calls.
        :param function_to_retry: The function to retry on timeout.
        :param response_timeout: The time in seconds that the function should return a response.
        :param max_retries: The maximum amount of times the function should be retried before raising the error.
        :param kwargs: Any key word arguments required for the calling function
        :return: The return object of the given function to retry.
        """
        for attempt in range(max_retries):
            try:
                response = function_to_retry(response_timeout=response_timeout, **kwargs)
            except requests.exceptions.Timeout:
                logging.warning(f"Retrying a timed out call to url --> {self.base_api_url}{kwargs['url_extension']}")
                response_timeout *= 2
                continue
            else:
                break
        else:
            raise requests.exceptions.Timeout

        return response

    def raw_get_request(self, url_extension: str, response_timeout: float = 5.0) -> requests.Response:

        response = requests.get(url=f"{self.base_api_url}{url_extension}",
                                headers=self.headers,
                                timeout=response_timeout)

        return response

    def raw_post_request(self, url_extension: str, response_timeout: float = 5.0,
                         payload: Dict = None) -> requests.Response:

        response = requests.post(url=f"{self.base_api_url}{url_extension}",
                                 data=payload,
                                 headers=self.headers,
                                 timeout=response_timeout)

        return response

    def get(self, url_extension: str, response_timeout: float = 5.0,
            max_retries: int = 3) -> requests.Response:
        """
        Function to perform get request, with retry functionality on timeout.
        :param url_extension: extension to the base url to call.
        :param response_timeout: time in seconds to halt the request if no response has been returned.
        :param max_retries: amount of times to retry before raising error if timeout seconds exceeded.
        :return: requests response object
        """
        try:
            return self.retry_on_timeouts(self.raw_get_request,
                                          response_timeout,
                                          max_retries,
                                          url_extension=url_extension)
        except requests.exceptions.Timeout as e:
            logging.exception(
                f"Timeout max. retries of {max_retries} exceeded unsuccessfully to {self.base_api_url}{url_extension}")
            raise e
        except requests.exceptions.RequestException as e:
            logging.exception(f"Get call to {self.base_api_url}{url_extension} failed --> {e}")
            raise e

    def post(self, url_extension: str, response_timeout: float = 5.0, max_retries: int = 3,
             payload: Dict = None) -> requests.Response:
        """
        Function to perform post request, with retry functionality on timeout.
        :param url_extension: extension to the base url to call.
        :param response_timeout: time in seconds to halt the request if no response has been returned.
        :param max_retries: amount of times to retry before raising error if timeout seconds exceeded.
        :param payload: data to be passed to the API.
        :return: requests response object
        """
        try:
            return self.retry_on_timeouts(self.raw_post_request,
                                          response_timeout,
                                          max_retries,
                                          url_extension=url_extension,
                                          payload=payload)
        except requests.exceptions.Timeout as e:
            logging.exception(
                f"Timeout max. retries of {max_retries} exceeded unsuccessfully to {self.base_api_url}{url_extension}")
            raise e
        except requests.exceptions.RequestException as e:
            logging.exception(f"Post call to {self.base_api_url}{url_extension} failed --> {e}")
            raise e
