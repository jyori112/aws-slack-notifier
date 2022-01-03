import os
from datetime import date
import unittest
from unittest.mock import patch

from functions import notify_bill
from functions.slack import Slack
from functions.cost_explorer import CostExplorer
from functions.datetime_range import DatetimeRange

class TestDaily(unittest.TestCase):
    @patch('functions.credential.get_secrets', return_value={"SLACK_WEBHOOK_URL": os.environ["SLACK_WEBHOOK_URL"]})
    def test_daily_report_sends_slack_message(self, mock):
        with patch.object(Slack, 'post', return_value=None) as post:
            with patch.object(CostExplorer, 'report', return_value={"AWS Secrets Manager": 1.42}) as report:
                notify_bill.daily({
                    "time": "2021-12-02T09:00:00Z"
                }, {})

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
                                "text": "*Total Price:* 1.42 USD"
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
        post.assert_called_once_with(payload)

        report.assert_called_once_with(DatetimeRange(start=date(2021, 12, 1),
                                                     end=date(2021, 12, 2)))

    @patch('functions.credential.get_secrets', return_value={"SLACK_WEBHOOK_URL": os.environ["SLACK_WEBHOOK_URL"]})
    def test_daily_report_with_multi_service(self, mock):
        with patch.object(Slack, 'post', return_value=None) as post:
            with patch.object(CostExplorer, 'report', return_value={"AWS Secrets Manager": 1.42, "EC2": 0.5}) as report:
                notify_bill.daily({
                    "time": "2021-12-02T09:00:00Z"
                }, {})

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
                                "text": "*Total Price:* 1.92 USD"
                            }
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Service:*\nAWS Secrets Manager:\nEC2:"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*Cost:*\n1.42 USD\n0.50 USD"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        post.assert_called_once_with(payload)