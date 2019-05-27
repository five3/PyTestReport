from .HTMLTestRunner import HTMLTestRunner


def make_report(stream, data, theme=None,
                stylesheet=None, htmltemplate=None, javascript=None):
    test_runner = HTMLTestRunner(stream, theme=theme, stylesheet=stylesheet,
                                htmltemplate=htmltemplate, javascript=javascript)
    data['stylesheet'] = test_runner.get_stylesheet()
    data['javascript'] = test_runner.get_javascript()
    return test_runner.generate_report(data)
