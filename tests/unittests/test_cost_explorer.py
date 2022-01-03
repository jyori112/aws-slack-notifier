import os
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

import boto3

from functions.cost_explorer import CostExplorer
from functions.datetime_range import DatetimeRange


class TestCostExplorer(unittest.TestCase):
    def test_post(self):
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

        report = ce.report(DatetimeRange(start=datetime(2021, 12, 1, 0, 0, 0),
                                         end=datetime(2021, 12, 2, 0, 0, 0)))


        client.get_cost_and_usage.assert_called_with(TimePeriod={"Start": "2021-12-01", "End": "2021-12-02"},
                                                     Granularity="MONTHLY",
                                                     Metrics=["AmortizedCost"],
                                                     GroupBy=[{ 'Type': "DIMENSION", "Key": "SERVICE"}])
        self.assertEqual(report, {"AWS Secrets Manager": 1.42})

