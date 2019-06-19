import json
import unittest

import pytest_Demo
from pytestreport import TestRunner
from pytestreport.api import make_report


class TestReport(unittest.TestCase):
    def setUp(self):
        self.suite = unittest.TestSuite()
        self.suite.addTests(unittest.TestLoader().loadTestsFromModule(pytest_Demo))

    def test_default_report(self):
        with open('Default_Report.html', 'wb') as fp:
            runner = TestRunner(fp, title='默认主题', description='默认主题描述', verbosity=2)
            runner.run(self.suite)

    def test_legency_report(self):
        with open('Legency_Report.html', 'wb') as fp:
            runner = TestRunner(fp, title='默认主题', description='默认主题描述', verbosity=2,
                                theme='legency')
            result = runner.run(self.suite)
            print(json.dumps(result.pytestreport_data, ensure_ascii=False, indent=2))

    def test_api_report(self):
        data = {
            "generator": "PyTestReport 0.1.4",
            "title": "默认主题",
            "description": "默认主题描述",
            "report_summary": {
                "start_time": "2019-05-12 23:07:49",
                "duration": "0:00:00.002000",
                "status": {
                    "pass": 1,
                    "fail": 0,
                    "error": 0,
                    "skip": 0
                }
            },
            "report_detail": {
                "tests": [
                    {
                        "summary": {
                            "desc": "utDemo.UTestPass",
                            "count": 1,
                            "pass": 1,
                            "fail": 0,
                            "error": 0,
                            "skip": 0,
                            "cid": "c1",
                            "status": "pass"
                        },
                        "detail": [
                            {
                                "has_output": False,
                                "tid": "pt1.1",
                                "desc": "testTrue",
                                "output": "",
                                "status": "pass",
                                "status_code": 0
                            }
                        ]
                    }
                ],
                "count": "1",
                "pass": "1",
                "fail": "0",
                "error": "0",
                "skip": "0"
            }
        }
        with open('API_Report.html', 'wb') as fp:
            make_report(fp, data)


if __name__ == '__main__':
    unittest.main()

