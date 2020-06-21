# coding: utf-8
import codecs
import csv
import traceback

import time

import jieba

from common_func import DbProxy, SendMail

ZHEJIANG_PROVINCE = ['磐安县', '天台县', '秀城区', '绍兴市', '常山县', '文成县', '德清县', '平阳县', '黄岩区', '余姚市', '衢江区', '海宁市', '永嘉县', '云和县', '武义县', '滨江区', '嘉善县', '岱山县', '温岭市', '南浔区', '莲都区', '北仑区', '兰溪市', '宁波市', '萧山区', '桐乡市', '缙云县', '婺城区', '西湖区', '浙江省', '舟山市', '瓯海区', '象山县', '开化县', '遂昌县', '新昌县', '金华市', '建德市', '台州市', '龙湾区', '富阳市', '桐庐县', '温州市', '长兴县', '衢州市', '海盐县', '庆元县', '嵊泗县', '杭州市', '吴兴区', '上虞市', '金东区', '越城区', '嘉兴市', '丽水市', '平湖市', '江东区', '奉化市', '浦江县', '乐清市', '永康市', '诸暨市', '临海市', '瑞安市', '临安市', '绍兴县', '湖州市', '安吉县', '上城区', '宁海县', '玉环县', '镇海区', '普陀区', '景宁畲族自治县', '秀洲区', '拱墅区', '松阳县', '龙泉市', '淳安县', '定海区', '慈溪市', '江北区', '青田县', '洞头县', '嵊州市', '鄞州区', '鹿城区', '下城区', '海曙区', '路桥区', '三门县', '泰顺县', '义乌市', '柯城区', '椒江区', '江干区', '东阳市', '苍南县', '江山市', '仙居县', '龙游县', '余杭区']
NEIMENG_PROVINCE = ['翁牛特旗', '磴口县', '内蒙古', '海南区', '阿鲁科尔沁旗', '新巴尔虎右旗', '镶黄旗', '元宝山区', '科尔沁右翼前旗', '白云矿区', '阿拉善盟', '化德县', '红山区', '正蓝旗', '正镶白旗', '凉城县', '赛罕区', '呼和浩特市', '苏尼特右旗', '青山区', '固阳县', '兴安盟', '兴和县', '科尔沁左翼中旗', '鄂托克旗', '额济纳旗', '阿拉善左旗', '科尔沁区', '宁城县', '开鲁县', '乌海市', '卓资县', '牙克石市', '商都县', '五原县', '霍林郭勒市', '锡林郭勒盟', '新城区', '扎赉特旗', '松山区', '巴林左旗', '乌拉特前旗', '九原区', '鄂托克前旗', '扎鲁特旗', '鄂尔多斯市', '乌达区', '回民区', '巴彦淖尔市', '新巴尔虎左旗', '东乌珠穆沁旗', '土默特左旗', '达拉特旗', '太仆寺旗', '多伦县', '科尔沁右翼中旗', '武川县', '西乌珠穆沁旗', '东胜区', '清水河县', '乌审旗', '根河市', '托克托县', '察哈尔右翼后旗', '二连浩特市', '扎兰屯市', '海勃湾区', '巴林右旗', '鄂温克族自治旗', '阿荣旗', '奈曼旗', '达尔罕茂明安联合旗', '库伦旗', '临河区', '满洲里市', '杭锦后旗', '伊金霍洛旗', '林西县', '阿巴嘎旗', '杭锦旗', '土默特右旗', '克什克腾旗', '察哈尔右翼中旗', '赤峰市', '包头市', '陈巴尔虎旗', '乌拉特后旗', '突泉县', '丰镇市', '锡林浩特市', '察哈尔右翼前旗', '乌拉特中旗', '昆都仑区', '石拐区', '准格尔旗', '乌兰察布市', '鄂伦春自治旗', '和林格尔县', '呼伦贝尔市', '阿拉善右旗', '玉泉区', '东河区', '四子王旗', '集宁区', '通辽市', '莫力达瓦达斡尔族自治旗', '乌兰浩特市', '阿尔山市', '喀喇沁旗', '海拉尔区', '科尔沁左翼后旗', '敖汉旗', '额尔古纳市', '苏尼特左旗']



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
        self.filename_table_map={"bidding_info.csv": "bidding_list", "substation.csv": "station_list"}
        self.neimeng = "neimeng.csv"
        self.zhejiang = "zhejiang.csv"

    def init_filename(self):
        # time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # s_time = time.strftime(time_str, "%Y-%m-%d %H:%M:%S")
        # time_stamp = int(time.mktime(s_time))
        time_stamp=int(time.mktime(time.localtime())) - (24 * 60 * 60)
        file_name="bidding_info.csv"
        return file_name, time_stamp

    def get_num(self, tm):
        sql_str="select count(*) from bidding_list where tmp>{}".format(tm)
        sql_str1="select count(*) from station_list where tmp>{}".format(tm)
        res, rows=self.db.read_db(sql_str)
        res, rows1=self.db.read_db(sql_str1)
        # total = rows[0][0] + rows1[0][0]
        return rows[0][0], rows1[0][0]

    def write_title(self, filename):
        f=codecs.open(filename, 'w', 'utf_8_sig')
        writer=csv.writer(f)
        writer.writerow(['标题', '来源', '开始时间', '结束时间', '链接'])
        f.close()

    def judge_valid(self, name, title):
        seg_list = jieba.cut(title, cut_all=True)
        for item in seg_list:
            if len(item) > 1:
                if item in ZHEJIANG_PROVINCE and name==self.zhejiang:
                    return True
                elif item in NEIMENG_PROVINCE and name==self.neimeng:
                    return True
                else:
                    return False
            else:
                return False
        return False

    def write_neimeng_zhejiang(self, filename, tm):
        for src_name in self.src_list:
            f=codecs.open(filename, 'a', 'utf_8_sig')
            writer=csv.writer(f)
            bid_str="select title, start, end, href from bidding_list where src='{}' and tmp>{} order by tmp desc".format(src_name, tm)
            sta_str="select title, start, end, href from station_list where src='{}' and tmp>{} order by tmp desc".format(src_name, tm)
            print(bid_str)
            res, rows = self.db.read_db(bid_str)
            for row in rows:
                row_info=list(row)
                res = self.judge_valid(filename, row_info[0])
                if not res:
                    continue
                source=self.map_dict[src_name]
                row_info.insert(1, source)
                writer.writerow(row_info)
            res, rows2 = self.db.read_db(sta_str)
            for row in rows2:
                row_info=list(row)
                res = self.judge_valid(filename, row_info[0])
                if not res:
                    continue
                source=self.map_dict[src_name]
                row_info.insert(1, source)
                writer.writerow(row_info)
            f.close()
            print(rows)
            print(rows2)

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

    def send_email(self, filename, filename1, num1, num2, filename3, filename4):
        if num1 or num2:
            email=SendMail(filename, filename1, num1, num2, filename3, filename4)
            email.run()

    def run(self):
        filename, timestamp=self.init_filename()
        station_filename="substation.csv"
        num1, num2 = self.get_num(timestamp)
        self.write_title(filename)
        self.write_title(station_filename)
        self.write_title(self.neimeng)
        self.write_title(self.zhejiang)
        self.write_csv(filename, timestamp)
        self.write_csv(station_filename, timestamp)
        self.write_neimeng_zhejiang(self.neimeng, timestamp)
        self.write_neimeng_zhejiang(self.zhejiang, timestamp)
        try:
            self.send_email(filename, station_filename, num1, num2, self.neimeng, self.zhejiang)
        except:
            traceback.print_exc()


if __name__ == '__main__':
    wo=WriteSend()
    wo.run()
