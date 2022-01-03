from datetime import datetime
import unittest
from unittest.mock import patch

from functions import notify_bill
from functions.slack import Slack
from functions.cost_explorer import CostExplorer
from functions.datetime_range import DatetimeRange

class TestDaily(unittest.TestCase):
    def test_daily_report_sends_slack_message(self):
        with patch.object(Slack, 'post', return_value=None) as post:
            with patch.object(CostExplorer, 'report', return_value={"AWS Secrets Manager": 1.42}) as report:
                notify_bill.daily({
                    "time": "2021-12-02T09:00:00Z"
                }, {})

        post.assert_called_once_with({
            'attachments': [
                {
                    'color': '#36a64f',
                    'pretext': '2021/12/01の請求額は、1.42 USDです。',
                    'text': 'AWS Secrets Manager: 1.42 USD'
                }
            ]
        })

        report.assert_called_once_with(DatetimeRange(start=datetime(2021, 12, 1, 0, 0, 0),
                                                     end=datetime(2021, 12, 2, 0, 0, 0)))

    def test_daily_report_with_multi_service(self):
        with patch.object(Slack, 'post', return_value=None) as post:
            with patch.object(CostExplorer, 'report', return_value={"AWS Secrets Manager": 1.42, "EC2": 0.5}) as report:
                notify_bill.daily({
                    "time": "2021-12-02T09:00:00Z"
                }, {})

        post.assert_called_once_with({
            'attachments': [
                {
                    'color': '#36a64f',
                    'pretext': '2021/12/01の請求額は、1.92 USDです。',
                    'text': 'AWS Secrets Manager: 1.42 USD\nEC2: 0.5 USD'
                }
            ]
        })