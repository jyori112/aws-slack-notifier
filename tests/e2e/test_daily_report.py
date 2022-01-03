import os
import unittest
from unittest.mock import MagicMock, patch

from functions import notify_bill, credential
from functions.credential import Credential, get_secrets


class TestDailyReport(unittest.TestCase):
    @patch('functions.credential.get_secrets', return_value={"SLACK_WEBHOOK_URL": os.environ["SLACK_WEBHOOK_URL"]})
    def test_daily_report(self, mock):
        notify_bill.daily({
            "time": "2021-12-01T09:00:00Z"
        }, {})
