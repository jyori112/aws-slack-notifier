from datetime import date
import unittest
from unittest.mock import patch

import requests
from functions.cost_explorer import DailyReport

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

    def test_post_daily_report(self):
        slack = Slack("test_url")

        with patch.object(requests, 'post') as post:
            slack.post_daily_report(DailyReport(date=date(2021, 12, 1), costs={"AWS Secrets Manager": 1.42}))

        payload = {
            "username": "AWS Cost Notification",
            "icon_emoji": ":aws:",
            "attachments": [
                {
                    "color": "#36a64f",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Daily cost of 2021/12/01: 1.42 USD"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Service:*\nAWS Secrets Manager:"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*Cost:*\n1.42 USD"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        post.assert_called_once_with("test_url", json=payload)

