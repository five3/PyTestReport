import unittest

from utDemo import UTest
from pytestreport import TestRunner

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(UTest))

    with open('UTReport.html', 'wb') as fp:
        runner = TestRunner(fp, title='测试标题', description='测试描述', verbosity=2)
        result = runner.run(suite)
        print(result)
