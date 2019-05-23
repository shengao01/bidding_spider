# !/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
import time
import traceback
import logging
import pymysql
pymysql.install_as_MySQLdb()
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


class SendMail(object):
    def __init__(self, filenname):
        self.mail_host="smtp.exmail.qq.com"  # 设置服务器
        self.mail_user="****"  # 用户名
        self.mail_pass="****"  # 口令
        self.sender="****"
        self.receivers=["****"]
        self.message = MIMEMultipart()
        self.smtpObj = smtplib.SMTP()
        self.filenname = filenname

    def init_message(self, message):
        message['From']=Header("****", 'utf-8')
        message['To']=Header('运营<yunying>', 'utf-8')
        time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        subject='招标信息 ' + time_now + ' 获取更新'
        message['Subject']=Header(subject, 'utf-8')
        # 邮件正文内容
        content_1=MIMEText('    (此邮件为信息获取完成自动发送，如有任何建议可直接回复邮件，也可直接联系我。) \n', 'plain', 'utf-8')
        message.attach(content_1)

    def add_attach(self, message, file_name):
        att1=MIMEText(open('./' + file_name, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"]='application/octet-stream'
        att1["Content-Disposition"]='attachment; filename="' + file_name + '"'
        message.attach(att1)

    def run(self):
        self.init_message(self.message)
        self.add_attach(self.message, self.filenname)
        self.smtpObj.connect(self.mail_host, 25)  # 25为SMTP服务端口号
        self.smtpObj.login(self.mail_user, self.mail_pass)
        self.smtpObj.sendmail(self.sender, self.receivers, self.message.as_string())
        print("邮件发送成功")


"""
mail_host = "smtp.exmail.qq.com"  #设置服务器
mail_user = "zhangshg@tdhxkj.com"    #用户名
mail_pass = "TDHXtdhx2018"   #口令

sender = "zhangshg@tdhxkj.com"
receivers = ["zhangshg@tdhxkj.com"]

def init_mail(message):
    message['From'] = Header("张身高<zhangshg@tdhxkj.com>", 'utf-8')
    message['To'] =  Header('运营<yunying>', 'utf-8')
    time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    subject = '招标信息 ' + time_now + ' 获取更新'
    message['Subject'] = Header(subject, 'utf-8')
    # 邮件正文内容
    content_1 = MIMEText('    (此邮件为信息获取完成自动发送，如有任何建议可直接回复邮件，也可直接联系我。) \n', 'plain', 'utf-8')
    message.attach(content_1)


def add_attcah(message, file_name):
    # 构造附件
    att1 = MIMEText(open('./'+file_name, 'rb').read(), 'base64', 'utf-8')
    att1["Content-Type"] = 'application/octet-stream'
    att1["Content-Disposition"] = 'attachment; filename="' + file_name + '"'
    message.attach(att1)


def send_mail(file_name="bidding_info.csv"):
    # 创建一个带附件的邮件
    msg = MIMEMultipart()
    init_mail(msg)
    add_attcah(msg, file_name)
    smtpObj = smtplib.SMTP()
    smtpObj.connect(mail_host, 25)    # 25为SMTP服务端口号
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, msg.as_string())
    print("邮件发送成功")
"""


class DbProxy(object):
    def __init__(self):
        self.connect_status=1
        self.reconnect_times=0
        self.cur=None
        try:
            self.conn=pymysql.connect(host='192.168.81.4', port=3306, user='root', passwd='123456', db='bidding_info')
        except:
            logging.error('connet mysql error')
            logging.error(traceback.format_exc())
            self.connect_status=0
            return
        self.cur=self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()
        return

    def check_db_errno(self, errno):
        if errno == 29 or errno == 1146 or errno == 1194 or errno == 1030 or errno == 1102 or errno == 1712:
            return True
        return False

    def write_db(self, sqlstr):
        try:
            self.cur.execute(sqlstr)
        except pymysql.Error as e:
            try:
                errno=e.args[0]
                errinfo=e.args[1]
                logging.error("write_db error, cmd=%s,errno=[%d],errinfo=%s", sqlstr, errno, errinfo)
            except IndexError:
                logging.error('write_db error')
                logging.error(traceback.format_exc())

            if self.reconnect_times < 5:
                self.reconnect_times+=1
                res=self.reconnect()
                # res = self.write_db(sqlstr)
                if res == 0:
                    self.reconnect_times=0
                else:
                    time.sleep(0.2)
                return res
            else:
                self.reconnect_times=0
                return 1
        try:
            self.conn.commit()
        except:
            logging.error("conn commit fail!!")
            logging.error(traceback.format_exc())
        return 0

    def read_db(self, sqlstr):
        try:
            self.cur.execute(sqlstr)
            rows=self.cur.fetchall()
        except pymysql.Error as e:
            try:
                errno=e.args[0]
                errinfo=e.args[1]
                if self.check_db_errno(errno):
                    logging.error("make mysql_check_error.flag")
                logging.error("read_db error: cmd=%s,errno=[%d],errinfo=%s", sqlstr, errno, errinfo)
            except IndexError:
                logging.error('read_db error')
                logging.error(traceback.format_exc())

            if self.reconnect_times < 5:
                self.reconnect_times+=1
                self.reconnect()
                res, rows=self.read_db(sqlstr)
                if res == 0:
                    self.reconnect_times=0
                else:
                    time.sleep(0.2)
                return res, rows
            else:
                self.reconnect_times=0
                rows=[]
                return 1, rows
        return 0, rows

    def execute(self, sqlstr):
        try:
            self.cur.execute(sqlstr)
        except pymysql.Error as e:
            try:
                errno=e.args[0]
                errinfo=e.args[1]
                if self.check_db_errno(errno):
                    logging.error("make mysql_check_error.flag")
                logging.error("execute error: cmd=%s,errno=[%d],errinfo=%s", sqlstr, errno, errinfo)
            except IndexError:
                logging.error("execute error, cmd=%s", sqlstr)
                logging.error(traceback.format_exc())

            if self.reconnect_times < 5:
                self.reconnect_times+=1
                self.reconnect()
                res, self.cur=self.execute(sqlstr)
                if res == 0:
                    self.reconnect_times=0
                return res, self.cur
            else:
                self.reconnect_times=0
                return 1, self.cur
        return 0, self.cur

    def get_connect_status(self):
        return self.connect_status

    def reconnect(self):
        try:
            self.cur.close()
            self.conn.close()
        except:
            logging.error(traceback.format_exc())
        try:
            self.conn=pymysql.connect(host='192.168.81.4', port=3306, user='root', passwd='123456',
                                      db='bidding_info')
        except:
            logging.error('connet mysql error')
            logging.error(traceback.format_exc())
            self.connect_status=0
            return
        self.cur=self.conn.cursor()
        self.connect_status=1
        logging.info("DbProxy reconnect ok")
