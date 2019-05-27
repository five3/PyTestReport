import os
import time
import datetime


def pytest_addoption(parser):
    group = parser.getgroup('terminal reporting')
    group.addoption('--html', action='store', dest='htmlpath',
                    metavar='path', default=None,
                    help='create html report file at given path.')
    group.addoption('--self-contained-html', action='store_true',
                    help='create a self-contained html file containing all '
                    'necessary styles, scripts, and images - this means '
                    'that the report may not render or function where CSP '
                    'restrictions are in place (see '
                    'https://developer.mozilla.org/docs/Web/Security/CSP)')
    group.addoption('--css', action='append', metavar='path', default=[],
                    help='append given css file content to report style file.')


def pytest_configure(config):
    htmlpath = config.getoption('htmlpath')
    if htmlpath:
        for csspath in config.getoption('css'):
            open(csspath)
        if not hasattr(config, 'slaveinput'):
            # prevent opening htmlpath on slave nodes (xdist)
            config._html = HTMLReport(htmlpath, config)
            config.pluginmanager.register(config._html)


def pytest_unconfigure(config):
    html = getattr(config, '_html', None)
    if html:
        del config._html
        config.pluginmanager.unregister(html)


class HTMLReport(object):

    def __init__(self, logfile, config):
        logfile = os.path.expanduser(os.path.expandvars(logfile))
        self.logfile = os.path.abspath(logfile)
        self.test_logs = []
        self.results = []
        self.errors = self.failed = 0
        self.passed = self.skipped = 0
        self.xfailed = self.xpassed = 0
        has_rerun = config.pluginmanager.hasplugin('rerunfailures')
        self.rerun = 0 if has_rerun else None
        self.self_contained = config.getoption('self_contained_html')
        self.config = config

    def _appendrow(self, outcome, report):
        result = self.TestResult(outcome, report, self.logfile, self.config)
        index = bisect.bisect_right(self.results, result)
        self.results.insert(index, result)
        self.test_logs.insert(index, tbody)

    def append_passed(self, report):
        if report.when == 'call':
            if hasattr(report, "wasxfail"):
                self.xpassed += 1
                self._appendrow('XPassed', report)
            else:
                self.passed += 1
                self._appendrow('Passed', report)

    def append_failed(self, report):
        if getattr(report, 'when', None) == "call":
            if hasattr(report, "wasxfail"):
                # pytest < 3.0 marked xpasses as failures
                self.xpassed += 1
                self._appendrow('XPassed', report)
            else:
                self.failed += 1
                self._appendrow('Failed', report)
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

    def _generate_report(self, session):
        suite_stop_time = time.time()
        suite_time_delta = suite_stop_time - self.suite_start_time
        numtests = self.passed + self.failed + self.xpassed + self.xfailed
        generated = datetime.datetime.now()
        environment = self._generate_environment(session.config)

    def _generate_environment(self, config):
        if not hasattr(config, '_metadata') or config._metadata is None:
            return []

        metadata = config._metadata
        environment = [html.h2('Environment')]
        rows = []

        keys = [k for k in metadata.keys()]
        if not isinstance(metadata, OrderedDict):
            keys.sort()

        for key in keys:
            value = metadata[key]
            if isinstance(value, basestring) and value.startswith('http'):
                value = html.a(value, href=value, target='_blank')
            elif isinstance(value, (list, tuple, set)):
                value = ', '.join((str(i) for i in value))
            rows.append(html.tr(html.td(key), html.td(value)))

        environment.append(html.table(rows, id='environment'))
        return environment

    def _save_report(self, report_content):
        dir_name = os.path.dirname(self.logfile)
        assets_dir = os.path.join(dir_name, 'assets')

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if not self.self_contained and not os.path.exists(assets_dir):
            os.makedirs(assets_dir)

        with open(self.logfile, 'w', encoding='utf-8') as f:
            f.write(report_content)
        if not self.self_contained:
            style_path = os.path.join(assets_dir, 'style.css')
            with open(style_path, 'w', encoding='utf-8') as f:
                f.write(self.style_css)

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
        self.suite_start_time = time.time()

    def pytest_sessionfinish(self, session):
        report_data = self._generate_report(session)
        self._save_report(report_data)

    def pytest_terminal_summary(self, terminalreporter):
        terminalreporter.write_sep('-', 'generated html file: {0}'.format(
            self.logfile))
