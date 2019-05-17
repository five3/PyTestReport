"""
A TestRunner for use with the Python unit testing framework. It
generates a HTML report to show the result at a glance.
The simplest way to use this is to invoke its main method. E.g.
    import unittest
    import pytestreport
    ... define your tests ...
    if __name__ == '__main__':
        pytestreport.main()
For more customization options, instantiates a HTMLTestRunner object.
HTMLTestRunner is a counterpart to unittest's TextTestRunner. E.g.
    # output to a file
    fp = file('my_report.html', 'wb')
    runner = pytestreport.HTMLTestRunner(
                stream=fp,
                title='My unit test',
                description='This demonstrates the report output by HTMLTestRunner.'
                )
    # Use an external stylesheet.
    # See the Template_mixin class for more customizable options
    runner.STYLESHEET_TMPL = '<link rel="stylesheet" href="my_stylesheet.css" type="text/css">'
    # run the test
    runner.run(my_test_suite)
------------------------------------------------------------------------
Copyright (c) 2004-2007, Wai Yip Tung
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name Wai Yip Tung nor the names of its contributors may be
  used to endorse or promote products derived from this software without
  specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# URL: http://tungwaiyip.info/software/HTMLTestRunner.html

__original_author__ = "Wai Yip Tung"
__update_author__ = "Xiaowu Chen"
__version__ = "0.1.4"

"""
0.1.0:
use Jinjia2 as template engine; 
html、style、js separate as standalone, and can be recover by specified a file;
can be install as Python Lib, and setup with `pip`;
can be use in command、as lib、as webservice、with unittest;
0.1.2:
modify the default theme
0.1.3:
htmltestrunner with fp
modify default theme template
0.1.4:
view on github
0.1.5:
can be import as lib for un-unittest framework
can be run and work with command line 
can be run as web service and work with http post method
"""

import datetime
import io
import os
import sys
import unittest
from xml.sax import saxutils
from jinja2 import Environment, PackageLoader

# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing. Output
# sent to sys.stdout and sys.stderr are automatically captured. However
# in some cases sys.stdout is already cached before HTMLTestRunner is
# invoked (e.g. calling logging.basicConfig). In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.
#   >>> logging.basicConfig(stream=HTMLTestRunner.stdout_redirector)
#   >>>

env = Environment(loader=PackageLoader('pytestreport', 'templates'))


class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(bytes(s, 'UTF-8'))

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)


class TemplateMixin(object):
    """
    Define a HTML template for report customerization and generation.
    Overall structure of an HTML report
    """

    DIR = os.path.dirname(os.path.abspath(__file__))
    STYLESHEET_DIR = os.path.join(DIR, 'static', 'css')
    JAVASCRIPT_DIR = os.path.join(DIR, 'static', 'js')

    STATUS = {
        0: 'pass',
        1: 'fail',
        2: 'error',
        3: 'skip'
    }

    DEFAULT_TITLE = 'PyTestReport Sample'
    DEFAULT_DESCRIPTION = ''

    HTML_TMPL = 'default.html'
    STYLESHEET_TMPL = 'default.css'
    JAVASCRIPT_TMPL = 'default.js'


TestResult = unittest.TestResult


class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.

    def __init__(self, verbosity=1):
        super().__init__()
        self.stdout0 = None
        self.stderr0 = None
        self.outputBuffer = None

        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.skip_count = 0

        self.verbosity = verbosity

        """
        result is a list of result in 4 tuple
        (
          result code (0: success; 1: fail; 2: error 3: skip),
          TestCase object,
          Test output (unicode string),
          stack trace,
        )
        """
        self.result = []

    def startTest(self, test):
        TestResult.startTest(self, test)

        # just one buffer for both stdout and stderr
        self.outputBuffer = io.BytesIO()
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1

        TestResult.addSuccess(self, test)
        output = self.complete_output()

        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('OK ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addFailure(self, test, err):
        self.failure_count += 1

        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()

        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('Fail  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')

    def addError(self, test, err):
        self.error_count += 1

        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()

        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('Error  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addSkip(self, test, err):
        self.skip_count += 1

        TestResult.addSkip(self, test, err)
        _, _exc_str = self.skipped[-1]
        output = self.complete_output()

        self.result.append((3, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('Skip  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('S')


class HTMLTestRunner(TemplateMixin):
    def __init__(self, stream=sys.stdout, verbosity=2, title=None, description=None,
                 stylesheet=None, htmltemplate=None, javascript=None):
        self.stream = stream
        self.verbosity = verbosity

        self.start_time = datetime.datetime.now()
        self.duration = None

        self.title = title or self.DEFAULT_TITLE
        self.description = description or self.DEFAULT_DESCRIPTION
        self.stylesheet = stylesheet or self.STYLESHEET_TMPL
        self.htmltemplate = htmltemplate or self.HTML_TMPL
        self.javascript = javascript or self.JAVASCRIPT_TMPL

    def run(self, test):
        """Run the given test case or test suite."""
        result = _TestResult(self.verbosity)
        test(result)

        self.duration = datetime.datetime.now() - self.start_time
        data = self.generate_data(result)
        html = self.generate_report(data)

        print(f'\nTime Elapsed: {self.duration}', file=sys.stderr)
        result.pytestreport_data = data
        result.pytestreport_html = html

        return result

    def generate_report(self, data):
        html_template = self.get_html_template()
        output = html_template.render(**data)

        self.stream.write(output.encode('utf-8'))
        return output

    def generate_data(self, result):
        return {
            'generator': 'PyTestReport %s' % __version__,
            'title': saxutils.escape(self.title),
            'description': saxutils.escape(self.description),
            'stylesheet': self.get_stylesheet(),
            'javascript': self.get_javascript(),
            'report_summary': self.get_report_summary(result),
            'report_detail': self._generate_report_detail(result)
        }

    def get_report_summary(self, result):
        start_time = str(self.start_time)[:19]
        duration = str(self.duration)
        status = {
            'pass': result.success_count,
            'fail': result.failure_count,
            'error': result.error_count,
            'skip': result.skip_count
        }
        return {
            'start_time': start_time,
            'duration': duration,
            'status': status
        }

    def get_stylesheet(self):
        with open(os.path.join(self.STYLESHEET_DIR, self.stylesheet), encoding='utf-8') as f:
            return f.read()

    def get_javascript(self):
        with open(os.path.join(self.JAVASCRIPT_DIR, self.javascript), encoding='utf-8') as f:
            return f.read()

    def get_html_template(self):
        return env.get_template(self.htmltemplate)

    def _generate_report_detail(self, result):
        tests = []
        sorted_result = self.sort_result(result.result)
        for cid, (cls, cls_results) in enumerate(sorted_result):
            # subtotal for a class
            np = nf = ne = ns = 0
            for n, t, o, e in cls_results:
                if n == 0:  # pass
                    np += 1
                elif n == 1:    # fail
                    nf += 1
                elif n == 2:    # error
                    ne += 1
                else:       # skip
                    ns += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = "%s.%s" % (cls.__module__, cls.__name__)
            doc = cls.__doc__.split("\n")[0] if cls.__doc__ else ""
            desc = '%s: %s' % (name, doc) if doc else name

            test = {
                'summary': {
                    'desc': desc,
                    'count': np + nf + ne + ns,
                    'pass': np,
                    'fail': nf,
                    'error': ne,
                    'skip': ns,
                    'cid': 'c%s' % (cid + 1),
                    'status': (ne and self.STATUS[2]) or (nf and self.STATUS[1]) or (ns and self.STATUS[3]) or self.STATUS[0]
                }, 'detail': []
            }

            for tid, (n, t, o, e) in enumerate(cls_results):
                test['detail'].append(self._generate_report_test(cid, tid, n, t, o, e))

            tests.append(test)

        return {
            'tests': tests,
            'count': str(result.success_count + result.failure_count + result.error_count + result.skip_count),
            'pass': str(result.success_count),
            'fail': str(result.failure_count),
            'error': str(result.error_count),
            'skip': str(result.skip_count)
        }

    def _generate_report_test(self, cid, tid, n, t, o, e):
        # e.g. 'pt1.1', 'ft1.1', etc
        has_output = bool(o or e)
        tid = self.STATUS[n][0] + 't%s.%s' % (cid + 1, tid + 1)
        name = t.id().split('.')[-1]
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name

        uo = o if isinstance(o, str) else o.decode('utf-8')
        ue = e if isinstance(e, str) else e.decode('utf-8')

        return {
            'has_output': has_output,
            'tid': tid,
            'desc': desc,
            'output': saxutils.escape(str(uo) + str(ue)),
            'status': self.STATUS[n],
            'status_code': n
        }

    @staticmethod
    def sort_result(result_list):
        rmap = {}
        for n, t, o, e in result_list:
            cls = t.__class__
            rmap.setdefault(cls, []).append((n, t, o, e))
        return rmap.items()


##############################################################################
# Facilities for running tests from the command line
##############################################################################

# Note: Reuse unittest.TestProgram to launch test. In the future we may
# build our own launcher to support more specific command line
# parameters like test title, CSS, etc.


class TestProgram(unittest.TestProgram):
    """
    A variation of the unittest.TestProgram. Please refer to the base
    class for command line parameters.
    """

    def runTests(self):
        # Pick HTMLTestRunner as the default test runner.
        # base class's testRunner parameter is not useful because it means
        # we have to instantiate HTMLTestRunner before we know self.verbosity.
        fp = None
        if self.testRunner is None:
            fp = open('PyTestReport.html', 'wb')
            self.testRunner = HTMLTestRunner(fp, verbosity=self.verbosity)
        unittest.TestProgram.runTests(self)
        if fp:
            fp.close()


main = TestProgram

##############################################################################
# Executing this module from the command line
##############################################################################

if __name__ == "__main__":
    main(module=None)
