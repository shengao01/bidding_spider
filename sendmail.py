# !/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

mail_host="smtp.qq.com"  #设置服务器
mail_user="401491197@qq.com"    #用户名
mail_pass="zsga19941014"   #口令

sender = 'sgzhang.5213@qq.com'
receivers = ['sgzhang.5213@gmail.com']

"""
# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
message = MIMEText('武汉研发 标书信息获取更新。。。', 'plain', 'utf-8')
message['From'] = Header("sgzhang<wuhanyanfa>", 'utf-8')  # 发送者
message['To'] = Header("guoxy<guoxy@tdhxkj.com>", 'utf-8')  # 接收者

time_now = time.ctime()
subject = time_now + '更新后的信息'
message['Subject'] = Header(subject, 'utf-8')

"""

#创建一个带附件的实例
message = MIMEMultipart()
message['From'] = Header("sgzhang<wuhanyanfa>", 'utf-8')
message['To'] =  Header("guoxy<yunying>", 'utf-8')
time_now = time.ctime()
subject = time_now + 'Python bidding message.'
message['Subject'] = Header(subject, 'utf-8')
 
#邮件正文内容
message.attach(MIMEText('标书信息获取更新……', 'plain', 'utf-8'))
 
# 构造附件1
att1 = MIMEText(open('/Users/zhangsg/Desktop/xiaobo.txt', 'rb').read(), 'base64', 'utf-8')
att1["Content-Type"] = 'application/octet-stream'
att1["Content-Disposition"] = 'attachment; filename="xiaobo.txt"'
message.attach(att1)
 
# 构造附件2，传送当前目录下的 runoob.txt 文件
att2 = MIMEText(open('/Users/zhangsg/code/spider_prj/bidding_spider/bidding_web.xlsx', 'rb').read(), 'base64', 'utf-8')
att2["Content-Type"] = 'application/octet-stream'
att2["Content-Disposition"] = 'attachment; filename="bidding_web.xlsx"'
message.attach(att2)



def main():
    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)    # 25为SMTP服务端口号
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


if __name__ == '__main__':
    main()
