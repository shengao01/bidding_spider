# coding: utf-8
import codecs
import csv
import traceback

import time
from common_func import DbProxy, SendCePingMail


class WriteSend(object):
    """
    write file from mysql to csv
    """
    def __init__(self):
        self.db=DbProxy()
        self.map_dict={"1": "国电招投标网https://cgdcbidding.dlzb.com/", "2": "国能e购www.neep.shop", "3": "华电集团www.chdtp.com.cn",
                       "4": "华能集团http://ec.chng.com.cn", "5": "神华招标网www.shenhuabidding.com.cn",
                       "6": "招标采购网www.zbytb.com", "7": "南方电网www.bidding.csg.cn", "8": "采购与招标网www.chinabidding.cn"}
        self.src_list=["1", "2", "3", "4", "5", "7", "8"]
        self.filename_table_map={"friend_bidding_info.csv": "friend_list"}

    def init_filename(self):
        # time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # s_time = time.strftime(time_str, "%Y-%m-%d %H:%M:%S")
        # time_stamp = int(time.mktime(s_time))
        if time.localtime().tm_hour == 17:
            time_stamp=int(time.mktime(time.localtime())) - (7 * 60 * 60)
        elif time.localtime().tm_hour == 10:
            time_stamp = int(time.mktime(time.localtime())) - (17 * 60 * 60)
        else:
            time_stamp = int(time.mktime(time.localtime())) - (24 * 60 * 60)
        file_name="friend_bidding_info.csv"
        return file_name, time_stamp

    def get_num(self, tm):
        sql_str="select count(*) from friend_list where tmp>{} and bId>116".format(tm)
        res, rows=self.db.read_db(sql_str)
        # total = rows[0][0] + rows1[0][0]
        return rows[0][0]

    def write_title(self, filename):
        f=codecs.open(filename, 'w', 'utf_8_sig')
        writer=csv.writer(f)
        writer.writerow(['标题', '来源', '开始时间', '结束时间', '链接'])
        f.close()

    def write_csv(self, filename, tm):
        """write detail info to csv file"""
        for src_name in self.src_list:
            f=codecs.open(filename, 'a', 'utf_8_sig')
            writer=csv.writer(f)
            sql_str="select title, start, end, href from {} where src='{}' and tmp>{} order by tmp desc".format(
                self.filename_table_map[filename], src_name, tm)
            print(sql_str)
            res, rows=self.db.read_db(sql_str)
            for row in rows:
                row_info=list(row)
                source=self.map_dict[src_name]
                row_info.insert(1, source)
                writer.writerow(row_info)
            f.close()
            print(rows)

    def send_email(self, filename, num1):
        if num1:
            email=SendCePingMail(filename, num1)
            email.run()

    def run(self):
        filename, timestamp=self.init_filename()
        num1 = self.get_num(timestamp)
        self.write_title(filename)
        self.write_csv(filename, timestamp)
        try:
            self.send_email(filename, num1)
        except:
            traceback.print_exc()


if __name__ == '__main__':
    wo=WriteSend()
    wo.run()
