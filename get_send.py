# coding: utf-8
import codecs
import csv
import time
from common_func import DbProxy, SendMail


class WriteFile(object):
    """
    write file from mysql to csv
    """
    def __init__(self):
        self.db = DbProxy()
        self.map_dict = {"1": "国电招投标网", "2": "国能e购", "3": "华电集团", "4": "华能集团", "5": "神华招标网"}
        self.src_list = ["1", "2", "3", "4", "5"]

    def init_filename(self):
        # time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # s_time = time.strftime(time_str, "%Y-%m-%d %H:%M:%S")
        # time_stamp = int(time.mktime(s_time))
        time_stamp = int(time.mktime(time.localtime()))
        file_name = "bidding_info.csv"
        return file_name, time_stamp

    def write_title(self, filename):
        f = codecs.open(filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['名称', '来源', '开始时间', '结束时间', '链接'])
        f.close()

    def write_csv(self, filename, tm):
        """write detail info to csv file"""
        for src_name in self.src_list:
            f = codecs.open(filename, 'a', 'utf_8_sig')
            writer = csv.writer(f)
            sql_str = "select title, start, end, href from bidding_list where src='{}' and tmp<{} order by tmp desc".format(src_name, tm)
            res, rows = self.db.read_db(sql_str)
            for row in rows:
                row_info = list(row)
                source = self.map_dict[src_name]
                row_info.insert(1, source)
                writer.writerow(row_info)
            f.close()
            print(rows)

    def send_email(self, filename):
        email = SendMail(filename)
        email.run()

    def run(self):
        filename, timestamp = self.init_filename()
        self.write_title(filename)
        self.write_csv(filename, timestamp)
        self.send_email(filename)


if __name__ == '__main__':
    wo = WriteFile()
    wo.run()
