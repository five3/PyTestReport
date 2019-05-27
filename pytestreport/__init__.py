import sys
import json

from .HTMLTestRunner import HTMLTestRunner as TestRunner, main
from .api import make_report

__all__ = ['TestRunner', 'main', 'shell', 'web']


def shell():
    arg_len = len(sys.argv)
    if arg_len == 1:
        print(f"""
        Usage:
            {sys.argv[0]} data.json [reportfile theme, htmltemplate, stylesheet, javascript]
        """)
        exit(1)
    data_file = 'data.json'
    report_file = 'PyTestReport.html'
    theme = htmltemplate = stylesheet = javascript = None
    if arg_len > 1:
        data_file = sys.argv[1]
    if arg_len > 2:
        report_file = sys.argv[2]
    if arg_len > 3:
        theme = sys.argv[3]
    if arg_len > 4:
        htmltemplate = sys.argv[4]
    if arg_len > 5:
        stylesheet = sys.argv[5]
    if arg_len > 6:
        javascript = sys.argv[6]

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        with open(report_file, 'wb') as fp:
            make_report(fp, data, theme=theme, htmltemplate=htmltemplate,
                        stylesheet=stylesheet, javascript=javascript)


def web():
    pass
