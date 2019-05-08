# !/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
import time
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

mail_host="smtp.qq.com"  #设置服务器
mail_user="sgzhang.5213@qq.com"    #用户名
mail_pass="****"   #口令


sender = 'sgzhang.5213@qq.com'
receivers = ['zhangshg@tdhxkj.com']

"""
# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
message = MIMEText('武汉研发 标书信息获取更新。。。', 'plain', 'utf-8')
message['From'] = Header("zhangshg<zhangshg@tdhxkj.com>", 'utf-8')  # 发送者
message['To'] = Header("guoxy<guoxy@tdhxkj.com>", 'utf-8')  # 接收者

time_now = time.ctime()
subject = time_now + '更新后的信息'
message['Subject'] = Header(subject, 'utf-8')
"""


def init_mail(message):
    message['From'] = Header("zhangshg<zhangshg@tdhxkj.com>", 'utf-8')
    message['To'] =  Header("yunxing<yunying>", 'utf-8')
    time_now = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    subject = '标书信息 ' + time_now + '更新'
    message['Subject'] = Header(subject, 'utf-8')

    #邮件正文内容
    content_1 = MIMEText('    邮件附件为经过关键词匹配后的各个网站标书信息统计。\n    此邮件为信息获取完成自动发送,如有任何建议可直接回复邮件,也可钉钉联系我。', 'plain', 'utf-8')
    message.attach(content_1)


def add_attcah(message, file_name):
    # 构造附件
    # att1 = MIMEText(open('./guodian_list.csv', 'rb').read(), 'base64', 'utf-8')
    att1 = MIMEText(open('./'+file_name, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    att1["Content-Disposition"] = 'attachment; filename="' + file_name + '"'
    message.attach(att1)


def send_mail():
    # 创建一个带附件的邮件
    msg = MIMEMultipart()
    init_mail(msg)
    # add_attcah(msg, "guoneng_list.csv")
    add_attcah(msg, "guodian_list.csv")
    add_attcah(msg, "guoneng_list.csv")
    add_attcah(msg, "huadian_list.csv")
    add_attcah(msg, "huaneng_list.csv")
    add_attcah(msg, "shenhua_list.csv")
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)    # 25为SMTP服务端口号
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, msg.as_string())
    print("邮件发送成功")


def main():
    try:
        send_mail()
    except:
        traceback.print_exc()
        print("Error: 无法发送邮件")


if __name__ == '__main__':
    main()
