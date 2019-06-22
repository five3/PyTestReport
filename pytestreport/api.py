import os
from subprocess import call

from .HTMLTestRunner import HTMLTestRunner
from .SendEmail import SendMail

__all__ = ["make_report", "make_image", "send_report"]


def make_report(stream, data, theme=None,
                stylesheet=None, htmltemplate=None, javascript=None):
    test_runner = HTMLTestRunner(stream, theme=theme, stylesheet=stylesheet,
                                htmltemplate=htmltemplate, javascript=javascript)
    data['stylesheet'] = test_runner.get_stylesheet()
    data['javascript'] = test_runner.get_javascript()
    return test_runner.generate_report(data)


def make_image(html_file, image_file, img_width="1350px"):
    """
    this function need `phantomjs` has been installed as well as run
    :param html_file: html report file path
    :param image_file: image file will be store
    :param img_width: set image file width
    :return:
    """
    js = os.path.join(os.path.dirname(__file__), "static", "js", "capture.js")
    cmds = ["phantomjs", js, html_file, image_file, img_width]
    output = call(cmds)
    if output == 0:
        print('make capture success!')
    else:
        print('make capture failed!')


def send_report(subject, html_file, image_file, frm, to, cc=[]):
    """
    发送邮件报告
    :param subject: 邮件主题
    :param html_file: 邮件html附件
    :param image_file: 邮件正文图片
    :param frm: 发件人邮箱
    :param to: 收件人邮箱列表
    :param cc: 抄送人邮箱列表
    :return:
    """
    send_mail = SendMail(frm=frm, to=to, cc=cc)
    attaches = [(html_file, 'text', 'html', os.path.basename(html_file), 1)]
    send_mail.send_as_image(subject, image_file, attaches=attaches)
