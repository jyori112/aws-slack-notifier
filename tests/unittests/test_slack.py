import unittest
from unittest.mock import patch

import requests

from functions.slack import Slack


class TestSlack(unittest.TestCase):
    def test_post(self):
        slack = Slack("test_url")

        with patch.object(requests, 'post') as post:
            payload = {
                'attachments': [
                    {
                        'color': '#36a64f',
                        'pretext': '2021/12/01の請求額は、1.42 USDです。',
                        'text': 'AWS Secrets Manager: 1.42 USD'
                    }
                ]
            }

            slack.post(payload)

        post.assert_called_once_with("test_url", json=payload)
