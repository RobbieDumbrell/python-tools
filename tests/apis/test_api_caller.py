import json
import unittest

import requests
import requests_mock

from tools.apis.api_caller import APICaller


class TestAPICaller(unittest.TestCase):

    def setUp(self) -> None:
        self.test_base_url = 'https://test'
        self.api_caller = APICaller(base_api_url=self.test_base_url)

    def test_request_retries_on_timeouts(self):
        mock_url_extension = '/extension'
        max_retries_expected = 3

        with requests_mock.Mocker() as mock:
            mock.get(url=self.test_base_url + mock_url_extension,
                     exc=requests.exceptions.Timeout)

            with self.assertRaises(requests.exceptions.Timeout):
                with self.assertLogs() as log_watcher:
                    self.api_caller.make_get_request(url_extension=mock_url_extension, response_timeout=0.1,
                                                     max_retries=max_retries_expected)

        expected_log_message = f"Retrying a timed out call to base-url --> {self.test_base_url + mock_url_extension}"
        expected_log_message_final = f"Timeout max. retries of {max_retries_expected} exceeded unsuccessfully"
        actual_retries_seen_from_logs = len(log_watcher.records)

        self.assertEqual(max_retries_expected + 1, actual_retries_seen_from_logs)
        assert log_watcher.records[0].getMessage() == expected_log_message
        assert log_watcher.records[1].getMessage() == expected_log_message
        assert log_watcher.records[2].getMessage() == expected_log_message
        assert log_watcher.records[3].getMessage() == expected_log_message_final

    def test_successful_get_request(self):
        mock_url_extension = '/extension'
        with requests_mock.Mocker() as mock:
            mock.get(url=self.test_base_url + mock_url_extension,
                     status_code=200,
                     text=json.dumps({'test_data': 'valid_data'}))
            response = self.api_caller.make_get_request(url_extension=mock_url_extension)

        self.assertIsNotNone(response)
        self.assertEqual(200, response.status_code)
        self.assertEqual({'test_data': 'valid_data'}, json.loads(response.text))
