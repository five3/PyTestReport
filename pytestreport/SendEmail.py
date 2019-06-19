#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具邮件基类
"""
import logging
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart


class SendMail(object):
    """该class用于发送邮件，是发送邮件的基类"""
    def __init__(self, frm, to, cc=None, server=None, port=25):
        self.mail_from = frm
        self.mail_to = to
        self.mail_cc = cc or []
        self.conn = None
        self.server = server or "114.251.201.21"
        self.port = port or 25
        self.mail_subject = ""
        self.mail_content = ""
        self.encoding = 'utf-8'
        self.attaches = []
        self.message_info = None

    def set_mail_from(self, mail_from):
        """
        设置发件人
        :param mail_from:
        :return:
        """
        self.mail_from = mail_from

    def set_mail_to(self, mail_to):
        """
        设置收件人
        :param mail_to:
        :return:
        """
        self.mail_to = mail_to

    def set_mail_cc(self, mail_cc):
        """
        设置抄送对象
        :param mail_cc:
        :return:
        """
        self.mail_cc = mail_cc

    def set_mail_subject(self, mail_subject):
        """
        设置邮件主题
        :param mail_subject:
        :return:
        """
        self.mail_subject = mail_subject

    def set_mail_content(self, mail_content):
        """
        设置邮件内容
        :param mail_content:
        :return:
        """
        self.mail_content = mail_content

    def mail_conn(self):
        """
        创建mail的链接
        :return:
        """
        try:
            self.conn = smtplib.SMTP(self.server, self.port)
        except Exception as e:
            print("mail server connect error!")
            logging.exception(e)
        else:
            print("mail server connect success!")

    def disconnect(self):
        """
        断开mail服务器链接
        """
        try:
            self.conn.close()
        except Exception as e:
            logging.exception(e)
        else:
            print("mail server close success!")

    def with_attaches(self, attaches=[]):
        attach_list = attaches or self.attaches

        for attach in attach_list:
            with open(attach[0], 'rb') as f:
                # 设置附件的MIME和文件名，这里是png类型:
                mime = MIMEBase(attach[1], attach[2], filename=attach[3])
                # 加上必要的头信息:
                mime.add_header('Content-Disposition', 'attachment', filename=attach[3])
                mime.add_header('Content-ID', '<%s>' % attach[4])
                mime.add_header('X-Attachment-Id', '%s' % attach[4])
                mime.set_payload(f.read())
                encoders.encode_base64(mime)
                self.message_info.attach(mime)

    def package_mail(self, _type):
        """
        组装邮件格式&内容
        """
        try:
            self.message_info = MIMEMultipart('alternative')
            self.message_info['From'] = self.mail_from
            self.message_info['To'] = ';'.join(self.mail_to)
            self.message_info['cc'] = ';'.join(self.mail_cc)
            self.message_info['subject'] = self.mail_subject

            if _type == 'html':
                att = MIMEText(self.mail_content, 'html', self.encoding)
            elif _type == 'image':
                self.with_attaches([(self.mail_content, 'image', 'png', 'report.png', 0)])
                att = MIMEText('<html><body><img src="cid:0"></body></html>', 'html', self.encoding)
            else:
                att = MIMEText(self.mail_content, 'plain', self.encoding)

            self.with_attaches()
            self.message_info.attach(att)
            self.conn.sendmail(self.mail_from, self.mail_to, self.message_info.as_string())
        except Exception as e:
            print("send mail faild!!!")
            logging.exception(e)
        else:
            print("send mail success!!!")

    def send_mail(self, subject, content, _type='html', encoding='utf-8', attaches=None):
        """
        发送邮件
        :return:
        """
        self.mail_subject = subject
        self.mail_content = content
        self.encoding = encoding
        if attaches:
            self.attaches = attaches

        self.mail_conn()
        if self.conn:
            self.package_mail(_type)
            self.disconnect()

    def send_as_text(self, subject, content, encoding=None, attaches=None):
        kwargs = {'_type': 'text'}
        if encoding:
            kwargs['encoding'] = encoding
        if attaches:
            kwargs['attaches'] = attaches

        self.send_mail(subject, content, **kwargs)

    def send_as_html(self, subject, content, encoding=None, attaches=None):
        kwargs = {'_type': 'html'}
        if encoding:
            kwargs['encoding'] = encoding
        if attaches:
            kwargs['attaches'] = attaches

        self.send_mail(subject, content, **kwargs)

    def send_as_image(self, subject, content, attaches=None):
        kwargs = {'_type': 'image'}
        if attaches:
            kwargs['attaches'] = attaches

        self.send_mail(subject, content, **kwargs)


if __name__ == "__main__":
    send_mail = SendMail()
    with open('d:/Default_Report.html', 'rb') as f:
        send_mail.send_mail('html test', f.read(), 'text')
        send_mail.send_mail('html test', f.read(), 'html')
    send_mail.send_mail('image test', 'D:/Default_Report.png', 'image')

    with open('d:/Default_Report.html', 'rb') as f:
        send_mail.send_as_text('text test', f.read())
        send_mail.send_as_html('html test', f.read())

    attaches = [("D:/Default_Report.html", 'text', 'html', 'report.html', 1)]
    send_mail.send_as_image('image test', 'D:/Default_Report.png', attaches=attaches)
