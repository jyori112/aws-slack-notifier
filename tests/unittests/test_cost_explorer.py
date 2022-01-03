import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import date

import boto3

from functions.cost_explorer import CostExplorer

class TestCostExplorer(unittest.TestCase):
    @patch('functions.credential.get_secrets', return_value={"SLACK_WEBHOOK_URL": os.environ["SLACK_WEBHOOK_URL"]})
    def test_daily_report(self, mock):
        client = boto3.client('ce', region_name=os.environ["AWS_REGION"])
        ce = CostExplorer(client)

        client.get_cost_and_usage = MagicMock(return_value={
            "ResultsByTime": [{
                'Groups': [{
                    'Keys': ["AWS Secrets Manager"],
                    'Metrics': {
                        'AmortizedCost': {
                            'Amount': "1.42"
                        }
                    }
                }]
            }]
        })

        report = ce.daily_report(date=date(2021, 12, 1))

        client.get_cost_and_usage.assert_called_with(TimePeriod={"Start": "2021-12-01", "End": "2021-12-02"},
                                                     Granularity="MONTHLY",
                                                     Metrics=["AmortizedCost"],
                                                     GroupBy=[{ 'Type': "DIMENSION", "Key": "SERVICE"}])

        self.assertEqual(report.date, date(2021, 12, 1))
        self.assertEqual(report.costs, {"AWS Secrets Manager": 1.42})

