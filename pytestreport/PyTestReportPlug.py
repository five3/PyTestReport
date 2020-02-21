import os
import time
import datetime
import bisect
from collections import OrderedDict

from pytestreport.api import make_report
from pytestreport import HTMLTestRunner


def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting')
    group.addoption('--pytest_report', action='store', dest='pytest_report', metavar='path', default=None,
                    help='create html report file at given path.')
    group.addoption('--pytest_title', action='store', dest='pytest_title', metavar='path', default="PyTestReport",
                    help='given title for report.')
    group.addoption('--pytest_desc', action='store', dest='pytest_desc', metavar='path', default="",
                    help='given desc for report..')
    group.addoption('--pytest_theme', action='store', dest='pytest_theme', metavar='path', default=None,
                    help='given theme for report.')
    group.addoption('--pytest_stylesheet', action='store', dest='pytest_stylesheet', metavar='path', default=None,
                    help='given css file path for report.')
    group.addoption('--pytest_htmltemplate', action='store', dest='pytest_htmltemplate', metavar='path', default=None,
                    help='given html file path for report.')
    group.addoption('--pytest_javascript', action='store', dest='pytest_javascript', metavar='path', default=None,
                    help='given js file path for report.')


def pytest_configure(config):
    htmlpath = config.getoption('pytest_report')
    if htmlpath:
        # for csspath in config.getoption('css'):
        #     open(csspath)
        if not hasattr(config, 'slaveinput'):
            # prevent opening htmlpath on slave nodes (xdist)
            config._html = HTMLReport(htmlpath, config)
            config.pluginmanager.register(config._html)


def pytest_unconfigure(config):
    html = getattr(config, '_html', None)
    if html:
        del config._html
        config.pluginmanager.unregister(html)


class TestResult:
    def __init__(self, outcome, report):
        self.outcome = outcome
        self.report = report

        # print(outcome)
        # print(report._to_json())

    def output(self, cid, tid):
        if self.outcome.startswith('X'):
            status = 'fail'
            status_code = 1
        elif self.outcome == "Passed":
            status = 'pass'
            status_code = 0
        elif self.outcome == "Failed":
            status = 'fail'
            status_code = 1
        elif self.outcome == "Error":
            status = 'error'
            status_code = 2
        elif self.outcome == "Skipped":
            status = 'skip'
            status_code = 3
        else:
            status = 'pass'
            status_code = 0

        output = "%s\r\n%s" % (self.outcome, self.report.longrepr) if status != 'pass' else ""

        return {
            "has_output": output and True or False,
            "tid": "test%s.%s.%s" % (status, cid, tid),
            "desc": self.report.nodeid.split("::")[-1],
            "output": output,
            "status": status,
            "status_code": status_code
        }


class HTMLReport(object):

    def __init__(self, html_file, config):
        html_file = os.path.expanduser(os.path.expandvars(html_file))
        self.html_file = os.path.abspath(html_file)
        self.results = []
        self.errors = self.failed = 0
        self.passed = self.skipped = 0
        self.xfailed = self.xpassed = 0
        has_rerun = config.pluginmanager.hasplugin('rerunfailures')
        self.rerun = 0 if has_rerun else None
        self.config = config

    def _appendrow(self, outcome, report):
        result = TestResult(outcome, report)
        self.results.append(result)

    def append_passed(self, report):
        if report.when == 'call':
            if hasattr(report, "wasxfail"):
                # pytest < 3.0 marked xpasses as failures
                self.xpassed += 1
                self._appendrow('XPassed', report)
            else:
                self.passed += 1
                self._appendrow('Passed', report)

    def append_failed(self, report):
        if getattr(report, 'when', None) == "call":
            if hasattr(report, "wasxfail"):
                self.xfailed += 1
                self._appendrow('XFailed', report)
            else:
                message = report.longrepr.reprcrash.message
                if message.startswith('assert'):    # assert Error
                    self.failed += 1
                    self._appendrow('Failed', report)
                else:
                    self.errors += 1
                    self._appendrow('Error', report)
        else:
            self.errors += 1
            self._appendrow('Error', report)

    def append_skipped(self, report):
        if hasattr(report, "wasxfail"):
            self.xfailed += 1
            self._appendrow('XFailed', report)
        else:
            self.skipped += 1
            self._appendrow('Skipped', report)

    def append_other(self, report):
        # For now, the only "other" the plugin give support is rerun
        self.rerun += 1
        self._appendrow('Rerun', report)

    def _generate_detail(self):
        tests = []
        sorted_result = self.sort_result()
        for cid, (cls, cls_results) in enumerate(sorted_result, 1):
            # subtotal for a class
            np = nf = ne = ns = 0
            for result in cls_results:
                if result.outcome == "Passed":  # pass
                    np += 1
                elif result.outcome in ["Failed", "XPassed", "XFailed"]:    # fail
                    nf += 1
                elif result.outcome == "Error":    # error
                    ne += 1
                elif result.outcome == "Skipped":       # skip
                    ns += 1

            # format class description
            name = cls
            doc = ""
            desc = '%s: %s' % (name, doc) if doc else name

            test = {
                'summary': {
                    'desc': desc,
                    'count': np + nf + ne + ns,
                    'pass': np,
                    'fail': nf,
                    'error': ne,
                    'skip': ns,
                    'cid': 'testclass%s' % cid,
                    'status': (ne and "error") or (nf and "fail") or (ns and "skip") or "pass"
                }, 'detail': []
            }

            for tid, result in enumerate(cls_results, 1):
                test['detail'].append(result.output(cid, tid))

            tests.append(test)

        return tests

    def sort_result(self):
        rmap = {}
        for result in self.results:
            cls = result.report.nodeid.split("::")[1]
            # cls = cls_path.split("/")[-1]
            rmap.setdefault(cls, []).append(result)
        return rmap.items()

    def _generate_report(self, session):
        suite_stop_time = datetime.datetime.now()
        duration = (suite_stop_time - self.suite_start_time).total_seconds()
        count = self.passed + self.failed + self.xpassed + self.xfailed + self.skipped + self.errors
        environment = self._generate_environment(session.config)
        tests = self._generate_detail()

        report_content = {
            "generator": "PyTestReport %s" % HTMLTestRunner.__version__,
            "title": "%s" % self.config.getoption('pytest_title'),
            "description": "%s" % self.config.getoption('pytest_desc'),
            "environment": environment,
            "report_summary": {
                "start_time": self.suite_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "duration": duration,
                "suite_count": len(tests),
                "status": {
                    "pass": self.passed,
                    "fail": self.failed + self.xfailed + self.xpassed,
                    "error": self.errors,
                    "skip": self.skipped,
                    "count": count
                }
            }, "report_detail": {
                "tests": tests,
                "count": count,
                "pass": self.passed,
                "fail": self.failed + self.xfailed + self.xpassed,
                "error": self.errors,
                "skip": self.skipped,
            }
        }

        return report_content

    def _generate_environment(self, config):
        if not hasattr(config, '_metadata') or config._metadata is None:
            return []

        return config._metadata

    def _save_report(self, report_content, theme=None, stylesheet=None, htmltemplate=None, javascript=None):
        dir_name = os.path.dirname(self.html_file)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        with open(self.html_file, 'wb') as fp:
            # make_report(fp, report_content, theme=theme, stylesheet=stylesheet, htmltemplate=htmltemplate,
            #             javascript=javascript)

            test_runner = HTMLTestRunner.HTMLTestRunner(fp, theme=theme, stylesheet=stylesheet,
                                         htmltemplate=htmltemplate, javascript=javascript)
            report_content['stylesheet'] = test_runner.get_stylesheet()
            report_content['javascript'] = test_runner.get_javascript()
            return test_runner.generate_report(report_content)

    def pytest_runtest_logreport(self, report):
        if report.passed:
            self.append_passed(report)
        elif report.failed:
            self.append_failed(report)
        elif report.skipped:
            self.append_skipped(report)
        else:
            self.append_other(report)

    def pytest_collectreport(self, report):
        if report.failed:
            self.append_failed(report)

    def pytest_sessionstart(self, session):
        self.suite_start_time = datetime.datetime.now()

    def pytest_sessionfinish(self, session):
        report_data = self._generate_report(session)
        theme = self.config.getoption('pytest_theme')
        stylesheet = self.config.getoption('pytest_stylesheet')
        htmltemplate = self.config.getoption('pytest_htmltemplate')
        javascript = self.config.getoption('pytest_javascript')
        self._save_report(report_data, theme, stylesheet, htmltemplate, javascript)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep('-', 'generated html file: {0}'.format(
            self.html_file))
