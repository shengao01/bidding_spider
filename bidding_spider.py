# coding: utf-8
import logging
import os
import requests
import csv
import codecs
import json
import time
import re
import jieba
import traceback
from lxml import etree
from common_func import DbProxy

key_words_list = ['测评', '安全', '工控', '主机', '等保', '加固', '信息', '监控', '防护', '攻防', '演练', '威胁', '入侵', '检测', '日志', '审计', '态势', '感知', '防火墙', '防病毒', '安防系统']
key_words_list_1 = ['变电','二次', '配电','省调']

waste_list = ['检测仪','流量计','安全阀','安全围栏','放大器','职业病','防雷','防化服','手套','道路','螺丝','除尘','风机','水质检测','安全鉴定','起重机械','食用','家具','空调','大气污染','设备维修','保养','交通安全','保养服务']


class BaseSpider(object):
    """
    基类,实现通用功能
   User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        }
        self.db = DbProxy()

    def _parse_url(self, url):
        resp = requests.get(url, headers=self.headers, timeout=20)
        return resp.content.decode()

    def parse_url(self, url, session=""):
        try:
            if session:
                resp = session.get(url, headers=self.headers, timeout=20)
                html_str = resp.content.decode()
            else:
                html_str = self._parse_url(url)
        except:
            html_str = None
        return html_str

    def get_login_session(self, url, form_data):
        session = requests.session()
        session.post(url,headers=self.headers,data=form_data)
        return session

    def post_url(self, url, form_data):
        try:
            resp = requests.post(url, data=form_data)
            html_str = resp.content.decode()
        except:
            html_str = None
        return html_str

    def write_db(self, cont_str, bidding_type):
        if cont_str[-1] == 1:
            title = cont_str[0]
            start_date = cont_str[2]
            end_date = cont_str[3]
            href = cont_str[4]
        elif cont_str[-1] == 2:
            title=cont_str[0]
            start_date=cont_str[3]
            end_date=cont_str[4]
            href=cont_str[5]
        elif cont_str[-1] == 3:
            title=cont_str[0]
            start_date=cont_str[4]
            end_date=""
            href=cont_str[5]
        elif cont_str[-1] == 4:
            title=cont_str[0]
            start_date=cont_str[2]
            end_date=""
            href=cont_str[3]
        elif cont_str[-1] == 5:
            title=cont_str[0]
            start_date=cont_str[3]
            end_date=""
            href=cont_str[4]
        elif cont_str[-1] == 7 or cont_str[-1] == 8:
            title=cont_str[0]
            start_date=cont_str[1]
            end_date=""
            href=cont_str[2]
        time_now = int(time.time())
        if bidding_type == 1:
            sql_str = "insert into bidding_list(title, src, start, end, href, tmp) values(\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(title, cont_str[-1], start_date, end_date, href, time_now)
        elif bidding_type == 2:
            sql_str = "insert into station_list(title, src, start, end, href, tmp) values(\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\")".format(title, cont_str[-1], start_date, end_date, href, time_now)
        else:
            sql_str = "a empty sql_str"
        print(sql_str)
        res = self.db.write_db(sql_str)
        if res == 1:
            return 1

    def write_file(self, cont_str, filename, num):
        seg_list = jieba.lcut(cont_str[0], cut_all=True)
        if len(set(seg_list+waste_list)) < (len(seg_list) + len(waste_list)):
            return
        for item in seg_list:
            if len(item) > 1 and item in key_words_list:
                # f = codecs.open(filename, 'a', 'utf_8_sig')
                # writer = csv.writer(f)
                # print(cont_str)
                # writer.writerow(cont_str)
                # f.close()
                cont_str.append(num)
                res = self.write_db(cont_str, 1)
                if res == 1:
                    return True
                break
            if len(item) > 1 and item in key_words_list_1:
                # f = codecs.open(filename, 'a', 'utf_8_sig')
                # writer = csv.writer(f)
                # print(cont_str)
                # writer.writerow(cont_str)
                # f.close()
                cont_str.append(num)
                res = self.write_db(cont_str, 2)
                if res == 1:
                    return True
                break



class GuoDianSpider(BaseSpider):
    """
    国家能源集团-国电招投标网的标书信息获取
    http://www.cgdcbidding.com/ggsb/index.jhtml
    """
    def __init__(self):
        super(GuoDianSpider, self).__init__()
        self.url_temp_list = ["http://www.cgdcbidding.com/ggsb/index_{}.jhtml",
                              "http://www.cgdcbidding.com/gggc/index_{}.jhtml",
                              "http://www.cgdcbidding.com/ggjg/index_{}.jhtml"]
        self.url_temp = "https://cgdcbidding.dlzb.com/page-{}.shtml"
        self.filename = 'guodian_list.csv'
        self.map_dict = {0: "货物", 1: "工程", 2: "服务"}
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['标题', '来源', '开始时间', '结束时间', '链接'])
        f.close()

    def get_total(self):
        total_list = []
        for url in self.url_temp_list:
            detail_html_str = self.parse_url(url.strip("_{}"))
            detail_html = etree.HTML(detail_html_str)
            total_str = detail_html.xpath('//div[@class="pagination"]/div/text()')[0]
            total_num = int(re.findall(r'1/(.*)?页', total_str)[0])
            total_list.append(total_num)
            # total_list.extend([url.format(i) for i in range(1, total_num+1)])
        print(total_list)
        # total_list = [2, 2, 2]
        # print(total_list)
        return total_list

    def get_content(self, detail_url, num):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            detail_html = etree.HTML(detail_html_str)
            content_list = detail_html.xpath('//div//ul[@class="cl_list"]//li')
            for li in content_list:
                item={}
                # item["src"] = self.map_dict[num]
                item["src"] = "工程"
                item["title"] = li.xpath("./a/@title")[0]
                item["start_date"] = li.xpath('./p/text()')[0]
                item["end_date"] = ""
                if item["end_date"]:
                    ta = time.strptime(item["end_date"], "%Y-%m-%d %H:%M")
                    ts = time.mktime(ta)
                    if ts < time.time():
                        print(item["end_date"])
                        return True
                item["href"] = li.xpath("./a/@href")[0]
                cont_str = [item['title'], item['src'], item['start_date'], item['end_date'], item['href']]
                print(item)
                self.write_file(cont_str, self.filename, 1)
                # self.write_db(cont_str,1)

    def run(self):
        # total_list = self.get_total()
        # for i, total in enumerate(total_list):
        #     j = 1
        #     while j < total+1:
        #         url = self.url_temp_list[i].format(j)
        #         print(url)
        #         res = self.get_content(url, i)
        #         if res:
        #             break
        #         j += 1
        #         time.sleep(0.1)
        for i in range(5):
            url = self.url_temp.format(i+1)
            print(url)
            res=self.get_content(url, i)
            if res:
                break
            time.sleep(0.1)


class GuoNengSpider(BaseSpider):
    """
    国家能源e购招标信息获取
    https://xbj.neep.shop/html/portal/notice.html
    """
    def __init__(self):
        super(GuoNengSpider, self).__init__()
        self.url_temp = "https://www.neep.shop/rest/service/routing/nouser/inquiry/quote/searchCmsArticleList?callback=1&quotDeadline=2019-04-19+15%3A13%3A25&noticeType=1&pageNo={}"
        self.filename = "guoneng_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['询价单名称', '询价单编号', '发布区域', '开始时间', '结束时间', '链接'])
        f.close()

    def get_content_list(self, detail_url):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            dict_str = detail_html_str[2:-1]
            item_dict = json.loads(dict_str)
            item_list = item_dict["data"]["rows"]
            for row in item_list:
                write_list = [row["inquireName"], row['inquireCode'], row['publishArea'], row['publishTimeString'],
                              row['quotDeadlineString'], row['articleUrl']]
                # print(write_list)
                if row['quotDeadlineString']:
                    ta = time.strptime(row['quotDeadlineString'], "%Y-%m-%d %H:%M:%S")
                    ts = time.mktime(ta)
                    if ts < time.time():
                        # print(row['quotDeadlineString'])
                        return True
                res = self.write_file(write_list, self.filename, 2)
                if res:
                    return True
            # print(len(item_list))
            # print(item_list[0])

    def get_total(self):
        url = self.url_temp.format(1)
        detail_html_str = self.parse_url(url)
        dict_str = detail_html_str[2:-1]
        item_dict = json.loads(dict_str)
        total_num = int(item_dict["data"]["total"])
        print(total_num)
        return total_num

    def run(self):
        total = self.get_total()
        url_list = [self.url_temp.format(i) for i in range(1, total+1)]
        for url in url_list:
            res = self.get_content_list(url)
            if res:
                return
            time.sleep(0.1)


class HuaDianSpider(BaseSpider):
    """
    华电集团电子商务平台采购信息/招标公告信息获取
    https://www.chdtp.com.cn/pages/wzglS/cgxx/caigou.jsp
    https://www.chdtp.com.cn/pages/wzglS/zbgg/zhaobiaoList.jsp
    """
    def __init__(self):
        super(HuaDianSpider, self).__init__()
        "https://www.chdtp.com.cn/webs/displayNewsCgxxAction.action?page.currentpage=1"
        self.url_temp = ["https://www.chdtp.com.cn/webs/displayNewsCgxxAction.action?page.currentpage={}",
                         "https://www.chdtp.com.cn/webs/queryWebZbgg.action?page.currentpage={}"]
        self.url_part = "https://www.chdtp.com.cn/staticPage/"
        self.map_dict = {0: "采购信息", 1: "招标信息"}
        self.filename = "huadian_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['名称', '来源', '状态', '单位', '开始时间', '链接'])
        f.close()

    def get_content_list(self, detail_url, num):  
        detail_html_str = self.parse_url(detail_url)
        if not detail_html_str:
            detail_html_str = " "
        # print(detail_html_str)
        detail_html = etree.HTML(detail_html_str)
        cont_list = detail_html.xpath("//table//tr")[1:-1]
        print(len(cont_list))
        for cont in cont_list:
            item = {}
            item["src"] = self.map_dict[num]
            item["title"] = cont.xpath("./td[2]//text()")[0]
            item["company"] = cont.xpath("./td[3]/text()")[0]  if cont.xpath("./td[3]/text()") else None
            # state = cont.xpath("./td[1]/span/text()")[0] if cont.xpath("./td[1]/span/text()") else None
            # item["state"] = state.strip().strip("\r\n\t")
            item["state"] = " "
            item["date"] = cont.xpath("./td[4]//text()")[0]
            date = re.findall(r'\[(.*?)\]', item["date"])
            if date:
                day = date[0]
                ta = time.strptime(day, "%Y-%m-%d")
                ts = time.mktime(ta)
                if int(time.time()) - int(ts) > 10 * 24 * 60 * 60:
                    return True
            href_str = cont.xpath("./td/a[1]/@href")[0]
            tail_url = re.findall(r"toGetContent\('(.*)'\)", href_str)[0]
            item["href"] = self.url_part + tail_url
            print(item)
            # if item["state"]:
            item["date"] = item["date"].replace("[","").replace("]","")
            write_list = [item["title"], item["src"], item["state"], item["company"], item["date"], item["href"]]
            self.write_file(write_list, self.filename, 3)

    def get_total(self):
        total_list = []
        for url in self.url_temp:
            url = url.format(1)
            print(url)
            detail_html_str = self.parse_url(url)
            if not detail_html_str:
                detail_html_str = " "
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            total_str = detail_html.xpath('//tr/td/span[@class="page"]/text()')[3]
            total_num = int(re.findall(r"1/(.*)? 页", total_str)[0])
            total_list.append(total_num)
        print(total_list)
        return total_list

    def run(self):
        total = self.get_total()
        # total[0] = 1
        for i in range(total[0]):
            url = self.url_temp[0].format(i+1)
            res = self.get_content_list(url, 0)
            if res:
                break
            time.sleep(0.1)
        for i in range(total[1]):
            url = self.url_temp[1].format(i + 1)
            res = self.get_content_list(url, 1)
            if res:
                break
            time.sleep(0.1)


class HuaNengSpider(BaseSpider):
    """
    华能集团
    http://ec.chng.com.cn/ecmall/more.do?start=0
    http://ec.chng.com.cn/ecmall/morelogin.do?type=107&start=0
    """
    def __init__(self):
        super(HuaNengSpider, self).__init__()

        self.url_temp_list = ["http://ec.chng.com.cn/ecmall/more.do?type=103&start={}&limit={}",
                              "http://ec.chng.com.cn/ecmall/more.do?start={}&limit={}"]
        self.url_part = "http://ec.chng.com.cn/ecmall/announcement/announcementDetail.do?announcementId={}"
        self.map_dict = {0: "询价公告", 1: "通知公告"}
        self.filename = "huaneng_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['名称', '来源', '开始时间', '链接'])
        f.close()

    def get_total(self):
        total_list = []
        for url in self.url_temp_list:
            url = url.format(0)
            detail_html_str = self.parse_url(url)
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            total_str = detail_html.xpath('//div[@class=" clearfix"]/input/@value')[0]
            total_num = int(total_str)
            total_list.append(total_num)
        print(total_list)
        return total_list

    def get_content(self, detail_url, num):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            cont_list = detail_html.xpath('//ul[@class="main_r_con"]/li')
            for cont in cont_list:
                item = {}
                item["src"] = self.map_dict[num]
                item["title"] = cont.xpath("./a/@title")[0]
                # item["company"] = cont.xpath("./td/a[2]/text()")[0]
                # item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"] = cont.xpath("./p/text()")[0]
                href_str = cont.xpath("./a/@href")[0]
                tail_url = re.findall(r"announcementClick\('(.*?)','", href_str)[0]
                item["href"] = self.url_part.format(tail_url)
                # print(item)
                write_list = [item["title"], item["src"], item["date"], item["href"]]
                self.write_file(write_list, self.filename, 4)

    def run(self):
        total_list = [10,10]
        # total_list = self.get_total()
        i = 0
        while i < total_list[0]:
            url = self.url_temp_list[0].format(i*50, 50)
            # print(url)
            self.get_content(url, 0)
            i += 1
            time.sleep(0.1)
        j = 0
        while j < total_list[1]:
            url = self.url_temp_list[1].format(j*50, 50)
            # print(url)
            self.get_content(url, 1)
            j += 1
            time.sleep(0.1)


class ShenHuaSpider(BaseSpider):
    """
    神华集团招标信息获取
    http://www.shenhuabidding.com.cn/bidweb/001/001002/001002001/1.html
    """
    def __init__(self):
        super(ShenHuaSpider, self).__init__()
        self.url_temp_list = ["http://www.shenhuabidding.com.cn/bidweb/001/001002/001002001/{}.html",
                              "http://www.shenhuabidding.com.cn/bidweb/001/001002/001002002/{}.html",
                              "http://www.shenhuabidding.com.cn/bidweb/001/001002/001002003/{}.html"]
        self.map_dict = {0: "货物", 1: "工程", 2: "服务"}
        self.url_part = "http://www.shenhuabidding.com.cn"
        self.filename = "shenhua_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['名称', '编号', '来源', '开始时间', '链接'])
        f.close()

    def get_total(self):
        total_list = []
        for url in self.url_temp_list:
            url = url.format(1)
            detail_html_str = self.parse_url(url)
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            total_str = detail_html.xpath('//div//ul/li[@class="zhuandao"]/text()')[0].strip()[2:]
            print(total_str)
            total_num = int(total_str)
            total_list.append(total_num)
        print(total_list)
        return total_list

    def get_content(self, detail_url, num):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            cont_list = detail_html.xpath('//div//ul[@class="right-items"]/li')
            for cont in cont_list:
                item = {}
                item["src"] = self.map_dict[num]
                item["title"] = cont.xpath(".//a/@title")[0]
                item["num"] = cont.xpath(".//a/span/text()")[0] if cont.xpath(".//a/span/text()") else " "
                # item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"] = cont.xpath("./span/text()")[0].strip()
                if item["date"]:
                    day = item["date"]
                    ta = time.strptime(day, "%Y-%m-%d")
                    ts = time.mktime(ta)
                    if int(time.time()) - int(ts) > 20 * 24 * 60 * 60:
                        return True
                href_str = cont.xpath(".//a[1]/@href")[0]
                item["href"] = self.url_part + href_str
                # print(item)
                write_list = [item["title"], item["num"], item["src"], item["date"], item["href"]]
                self.write_file(write_list, self.filename, 5)

    def run(self):
        total_list = self.get_total()
        for i, total in enumerate(total_list):
            j = 1
            while j < total+1:
                url = self.url_temp_list[i].format(j)
                print(url)
                if self.get_content(url, i):
                    break
                j += 1
                time.sleep(0.1)


class ZhaoCaiSpider(BaseSpider):
    """
    招标与采购网
    https://www.zbytb.com/gongcheng-1.html
    """
    def __init__(self):
        super(ZhaoCaiSpider, self).__init__()
        self.url_temp_list = ["https://www.zbytb.com/zb/search.php?page=1&kw={}".format(i) for i in key_words_list]
        self.url_part = ""
        self.login_url = "https://www.zbytb.com/member/login.php"
        self.form_data = {
            "forward": "https://www.zbytb.com/member/my.php",
            "username": "Tdhx2018",
            "password": "123456",
            "cookietime": 1,
            "submit": 1,
            "ajax": 1
            }
        self.map_dict = {0: "工程", 1: "货物", 2: "服务", 3: "电力", 4: "石油"}
        self.filename = "zhaocai_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['名称', '来源', '地区', '开始时间', '链接'])
        f.close()

    def get_total(self, session):
        total_list = []
        for url in self.url_temp_list:
            # url = url.format(1)
            try:
                detail_html_str = self.parse_url(url, session)
                if detail_html_str:
                    detail_html = etree.HTML(detail_html_str)
                    total_str = detail_html.xpath('//div[@class="pages"]//cite/text()')[0]
                    total_num = int(re.findall(r"条/(.*?)页", total_str)[0])
                    time.sleep(5)
            except:
                total_num = 1
            print(total_num)
            total_list.append(total_num)
        return total_list

    def get_content(self, detail_url, num, session):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url, session)
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            cont_list = detail_html.xpath('//tr[@class="hover_tr"]')
            for cont in cont_list:
                item = {}
                item["src"] = self.map_dict[num]
                item["title"] = cont.xpath("./td[2]/a/text()")[0]
                item["area"] = cont.xpath("./td[1]/a/text()")[0] if cont.xpath("./td[1]/a/text()") else " "
                # item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"] = cont.xpath("./td[4]/text()")[0].strip()
                item["href"] = cont.xpath("./td[2]/a/@href")[0].strip()
                # print(item)
                write_list = [item["title"], item["src"], item["area"], item["date"], item["href"]]
                self.write_file(write_list, self.filename, 6)

    def run(self):
        session=self.get_login_session(self.login_url, self.form_data)
        total_list = self.get_total(session)
        print(total_list)
        for i, total in enumerate(total_list):
            j = 1
            while j < total+1:
                url = self.url_temp_list[i].format(j)
                print(url)
                self.get_content(url, i, session)
                j += 1
                time.sleep(5)


class NanDianSpider(BaseSpider):
    """
    南方电网数据
    http://www.bidding.csg.cn
    """
    def __init__(self):
        super(NanDianSpider, self).__init__()
        self.filename = "nandian.csv"
        self.url_temp = "http://www.bidding.csg.cn/zbgg/index_{}.jhtml"
        self.url_part = "http://www.bidding.csg.cn"

    def get_content(self, detail_url):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            # print(detail_html_str)
            detail_html=etree.HTML(detail_html_str)
            cont_list = detail_html.xpath('//div[@class="BorderEEE NoBorderTop List1 Black14 Padding5"]/ul/li')
            for cont in cont_list:
                item = {}
                item["title"]=cont.xpath("./a/text()")[0]
                # item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"]=cont.xpath("./span/text()")[0].strip()
                print(item["date"])
                # if item["date"]:
                #     day=item["date"]
                #     ta=time.strptime(day, "%Y-%m-%d")
                #     ts=time.mktime(ta)
                #     if int(time.time()) - int(ts) > 60 * 24 * 60 * 60:
                #         return True
                href_str=cont.xpath("./a/@href")[0]
                item["href"]=self.url_part + href_str
                print(item)
                write_list = [item["title"], item["date"], item["href"]]
                self.write_file(write_list, self.filename, 7)

    def run(self):
        for i in range(20):
            url = self.url_temp.format(i+1)
            res = self.get_content(url)
            if res:
                break
            time.sleep(1)


class CaizhaoSpider(BaseSpider):
    """www.chinabidding.com,采购与招标网数据获取"""
    def __init__(self):
        super(CaizhaoSpider, self).__init__()
        self.filename = "caizhao.csv"
        self.url_temp = "http://www.chinabidding.cn/zbxx/zbgg/{}.html"
        self.url_part = "http://www.chinabidding.cn"

    def get_content(self, detail_url):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            # print(detail_html_str)
            detail_html=etree.HTML(detail_html_str)
            cont_list = detail_html.xpath('//div[@class="y_n_y fl"]//tr[@class="yj_nei"]')
            for cont in cont_list:
                item = {}
                item["title"]=cont.xpath(".//td/a/@title")[0].strip()
                # item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"]=cont.xpath(".//td/text()")[1].strip()
                # print(item["date"])
                href_str=cont.xpath(".//td/a/@href")[0]
                item["href"]=self.url_part + href_str
                print(item)
                write_list=[item["title"], item["date"], item["href"]]
                self.write_file(write_list, self.filename, 8)

    def run(self):
        for i in range(40):
            print("enter page===={}".format(i))
            url = self.url_temp.format(i+1)
            res = self.get_content(url)
            if res:
                break
            time.sleep(2)


if __name__ == '__main__':
    path = "./log.log"
    try:
        guodian=GuoDianSpider()
        guodian.run()
        os.system("echo \"guodian is running finished.\" >> %s" %  path)
    except:
        print("guodian run error...")
        print(traceback.format_exc())

    try:
        guoneng=GuoNengSpider()
        guoneng.run()
    except:
        print("guoneng run error...")
        print(traceback.format_exc())

    try:
        huadian=HuaDianSpider()
        huadian.run()
    except:
        print("huadian run error...")
        print(traceback.format_exc())

    try:
        huaneng=HuaNengSpider()
        huaneng.run()
    except:
        print("huaneng run error...")
        print(traceback.format_exc())

    try:
        shenhua=ShenHuaSpider()
        shenhua.run()
    except:
        print("shenhua run error...")
        print(traceback.format_exc())

    try:
        nandian=NanDianSpider()
        nandian.run()
    except:
        print("nandian run error...")
        print(traceback.format_exc())

    try:
        caizhao = CaizhaoSpider()
        caizhao.run()
    except:
        print("caizhao run error...")
        print(traceback.format_exc())

    # try:
    #     zhaocai=ZhaoCaiSpider()
    #     zhaocai.run()
    # except:
    #     print("zhaocai run error...")
    #     print(traceback.format_exc())

    time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    os.system("echo \"%s is running finished.\" >> %s" %(str(time_now), path))
