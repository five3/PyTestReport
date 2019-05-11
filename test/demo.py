import json
import unittest

import utDemo
from pytestreport import TestRunner

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromModule(utDemo))

    with open('UTReport.html', 'wb') as fp:
        runner = TestRunner(fp, title='默认主题', description='默认主题描述', verbosity=2)
                            # ,htmltemplate='legency.html', stylesheet='legency.css', javascript='legency.js')
        result = runner.run(suite)
        print(json.dumps(result, ensure_ascii=False))
