# coding: utf-8
import codecs
import csv
import time
from common_func import DbProxy, SendMail


class WriteSend(object):
    """
    write file from mysql to csv
    """
    def __init__(self):
        self.db = DbProxy()
        self.map_dict = {"1": "国电招投标网", "2": "国能e购", "3": "华电集团", "4": "华能集团", "5": "神华招标网", "6": "招标采购网", "7": "南方电网"}
        self.src_list = ["1", "2", "3", "4", "5", "7"]
        self.filename_table_map = {"bidding_info.csv": "bidding_list", "substation.csv": "station_list"}

    def init_filename(self):
        # time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # s_time = time.strftime(time_str, "%Y-%m-%d %H:%M:%S")
        # time_stamp = int(time.mktime(s_time))
        time_stamp = int(time.mktime(time.localtime())) - (24*60*60)
        if time_stamp < 1573185600:
            time_stamp = 1573194000
        file_name = "bidding_info.csv"
        return file_name, time_stamp

    def get_num(self, tm):
        sql_str="select count(*) from bidding_list where tmp>{}".format(tm)
        sql_str1="select count(*) from station_list where tmp>{}".format(tm)
        res, rows=self.db.read_db(sql_str)
        res, rows1=self.db.read_db(sql_str1)
        total = rows[0][0] + rows1[0][0]
        return total

    def write_title(self, filename):
        f = codecs.open(filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['标题', '来源', '开始时间', '结束时间', '链接'])
        f.close()

    def write_csv(self, filename, tm):
        """write detail info to csv file"""
        for src_name in self.src_list:
            f = codecs.open(filename, 'a', 'utf_8_sig')
            writer = csv.writer(f)
            sql_str = "select title, start, end, href from {} where src='{}' and tmp>{} order by tmp desc".format(self.filename_table_map[filename], src_name, tm)
            res, rows = self.db.read_db(sql_str)
            for row in rows:
                row_info = list(row)
                source = self.map_dict[src_name]
                row_info.insert(1, source)
                writer.writerow(row_info)
            f.close()
            print(rows)

    def send_email(self, filename, filename1, upnum):
        if upnum > 0:
            email = SendMail(filename, filename1, upnum)
            email.run()

    def run(self):
        filename, timestamp = self.init_filename()
        station_filename = "substation.csv"
        up_num = self.get_num(timestamp)
        self.write_title(filename)
        self.write_title(station_filename)
        self.write_csv(filename, timestamp)
        self.write_csv(station_filename, timestamp)
        self.send_email(filename,station_filename, up_num)


if __name__ == '__main__':
    wo = WriteSend()
    wo.run()
