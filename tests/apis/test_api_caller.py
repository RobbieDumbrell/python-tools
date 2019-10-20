import unittest

import requests

from tools.apis.api_caller import APICaller


class TestAPICaller(unittest.TestCase):

    def setUp(self) -> None:
        self.api_caller = APICaller(
            base_api_url='http://www.google.com:81/')  # this is a real google url that returns nothing infinitely

    def test_retry_on_timeouts(self):
        max_retries_expexted = 3

        with self.assertRaises(requests.exceptions.Timeout):
            with self.assertLogs() as log_watcher:
                self.api_caller.make_get_request(url_extension='', response_timeout=0.1,
                                                 max_retries=max_retries_expexted)

        expected_log_message = "Retrying a timed out call to base-url --> http://www.google.com:81/"
        actual_retries_seen_from_logs = len(log_watcher.records)

        self.assertEqual(max_retries_expexted, actual_retries_seen_from_logs)
        assert log_watcher.records[0].getMessage() == expected_log_message
        assert log_watcher.records[1].getMessage() == expected_log_message
        assert log_watcher.records[2].getMessage() == expected_log_message
