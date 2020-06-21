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
from common_var import *


class SendMail(object):
    def __init__(self, filenname, filename1, num1, num2, filename3, filename4):
        self.mail_host="smtp.exmail.qq.com"  # 设置服务器
        self.mail_user= MAIL_USER  # 用户名
        self.mail_pass= MAIL_PASSWD  # 口令
        self.sender= MAIL_USER
        # self.receivers=["zhangshg@tdhxkj.com"]
        self.receivers= RECEIVERS
        self.message = MIMEMultipart()
#        self.smtpObj = smtplib.SMTP_SSL(self.mail_host, 463)
        self.smtpObj = smtplib.SMTP()
        self.filenname = filenname
        self.filenname1 = filename1
        self.filenname3 = filename3
        self.filenname4 = filename4
        self.num = num1
        self.num2 = num2
        self.total = num1 + num2

    def init_message(self, message, num):
        message['From']=Header("张身高<{}>".format(MAIL_USER), 'utf-8')
        message['To']=Header('for运营<yunying>', 'utf-8')
        time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        subject='招标信息 ' + time_now + ' 获取更新(接前次数据)'
        message['Subject']=Header(subject, 'utf-8')
        # 邮件正文内容
        head = "    此次新增内容{}条(其中一般招标信息{}条, 变电站相关{}条),详情请查阅附件。\n".format(self.total,self.num,self.num2)
        content_1=MIMEText(head + "    bidding_info.csv信息筛选的关键字为: {},\n"
                                  "    substation.csv信息筛选的关键字为: {}。 \n    "
                                  "此邮件为信息获取完成自动发送，如有遇到任何问题可随时与我联系。 \n    "
                                  "(说明：浙江和内蒙两个省份信息为bidding_info和station_list.csv通过标题匹配对应省份下所有市区县名称的方式提取，可能存在数据为空的情况。）", 'plain', 'utf-8')
        # content_2=MIMEText(head + "    以下是sunstation.csv信息筛选的关键字列表: ['变电','二次','防病毒','入侵','省调','配电'], \n    如有需要可新增。\n    (此邮件为信息获取完成自动发送，如有任何建议可直接回复邮件，也可直接联系我。) \n", 'plain', 'utf-8')
        message.attach(content_1)

    def add_attach(self, message, file_name):
        att1=MIMEText(open('./' + file_name, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"]='application/octet-stream'
        att1["Content-Disposition"]='attachment; filename="' + file_name + '"'
        message.attach(att1)

    def run(self):
        self.init_message(self.message, self.num)
        self.add_attach(self.message, self.filenname)
        self.add_attach(self.message, self.filenname1)
        self.add_attach(self.message, self.filenname3)
        self.add_attach(self.message, self.filenname4)
        self.smtpObj.connect(self.mail_host, 25)  # 25为SMTP服务端口号
        self.smtpObj.login(self.mail_user, self.mail_pass)
        self.smtpObj.sendmail(self.sender, self.receivers, self.message.as_string())
        print("邮件发送成功")


class DbProxy(object):
    def __init__(self, db="bidding_info"):
        self.connect_status=1
        self.reconnect_times=0
        self.cur=None
        self.db_name = db
        try:
            self.conn=pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db=self.db_name)
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
            self.conn=pymysql.connect(host='localhost', port=3306, user='root', passwd='123456',
                                      db=self.db_name)
        except:
            logging.error('connet mysql error')
            logging.error(traceback.format_exc())
            self.connect_status=0
            return
        self.cur=self.conn.cursor()
        self.connect_status=1
        logging.info("DbProxy reconnect ok")
