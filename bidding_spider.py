import requests
import csv
import codecs
import json
import time
import re
import traceback
from lxml import etree


class BaseSpider(object):
    """
    基类,实现通用功能
    """
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
        }

    def _parse_url(self, url):
        resp = requests.get(url, headers=self.headers, timeout=20)
        return resp.content.decode()

    def parse_url(self, url):
        try:
            html_str = self._parse_url(url)
        except:
            html_str = None
        return html_str

    def post_url(self, url, form_data):
        try:
            resp = requests.post(url, data=form_data)
            html_str = resp.content.decode()
        except:
            html_str = None
        return html_str

    def write_file(self, cont_str, filename):
        f = codecs.open(filename, 'a', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(cont_str)
        f.close()


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
        self.filename = 'guodian_list.csv'
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['标题', '开始时间', '结束时间', '链接'])
        f.close()

    def get_url_list(self):
        url_list = []
        for url in self.url_temp_list:
            detail_html_str = self.parse_url(url.strip("_{}"))
            detail_html = etree.HTML(detail_html_str)
            total_str = detail_html.xpath('//div[@class="pagination"]/div/text()')[0]
            total_num = int(re.findall(r'1/(.*)?页', total_str)[0])
            print(total_num)
            url_list.extend([url.format(i) for i in range(1, total_num+1)])
        return url_list

    def get_content_list(self, detail_url):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            detail_html = etree.HTML(detail_html_str)
            content_list = detail_html.xpath('//div[@class="listbox"]//li')
            for li in content_list:
                item={}
                item["title"] = li.xpath("./a/@title")[0]
                item["start_date"] = li.xpath('./a//input/@value')[0]
                item["end_date"] = li.xpath('./a//input/@value')[1]
                item["href"] = li.xpath("./a/@href")[0]
                cont_str = list(item.values())
                print(cont_str)
                self.write_file(cont_str, self.filename)

    def run(self):
        url_list = self.get_url_list()
        for url in url_list:
            print("enter parse url: " + url)
            self.get_content_list(url)
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
                print(write_list)
                self.write_file(write_list, self.filename)
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
            self.get_content_list(url)
            time.sleep(0.1)


class HuaDianSpider(BaseSpider):
    """
    华电集团电子商务平台采购信息/招标公告信息获取
    https://www.chdtp.com.cn/pages/wzglS/cgxx/caigou.jsp
    https://www.chdtp.com.cn/pages/wzglS/zbgg/zhaobiaoList.jsp
    """
    def __init__(self):
        super(HuaDianSpider, self).__init__()
        self.url_temp = ["https://www.chdtp.com.cn/webs/displayNewsCgxxAction.action?page.currentpage={}",
                         "https://www.chdtp.com.cn/webs/queryWebZbgg.action?page.currentpage={}"]
        self.url_part = "https://www.chdtp.com.cn/staticPage/"
        self.map_dict = {0: "采购信息", 1: "招标信息"}
        self.filename = "huadian_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['来源', '名称', '单位', '询价', '开始时间', '链接'])
        f.close()

    def get_content_list(self, detail_url, num):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            cont_list = detail_html.xpath("//table//tr")[1:-1]
            for cont in cont_list:
                item = {}
                item["src"] = self.map_dict[num]
                item["title"] = cont.xpath("./td/a[1]/text()")[0]
                item["company"] = cont.xpath("./td/a[2]/text()")[0]
                item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"] = cont.xpath("./td[2]/span/text()")[0]
                href_str = cont.xpath("./td/a[1]/@href")[0]
                tail_url = re.findall(r"toGetContent\('(.*)'\)", href_str)[0]
                item["href"] = self.url_part + tail_url
                print(item)
                write_list = [item["src"], item["title"], item["company"], item["state"], item["date"], item["href"]]
                self.write_file(write_list, self.filename)
            # print(len(item_list))
            # print(item_list[0])

    def get_total(self):
        total_list = []
        for url in self.url_temp:
            url = url.format(1)
            detail_html_str = self.parse_url(url)
            detail_html = etree.HTML(detail_html_str)
            total_str = detail_html.xpath('//tr/td/span[@class="page"]/text()')[3]
            total_num = int(re.findall(r"1/(.*)? 页", total_str)[0])
            total_list.append(total_num)
        print(total_list)
        return total_list

    def run(self):
        total = self.get_total()
        for i in range(total[0]):
            url = self.url_temp[0].format(i+1)
            self.get_content_list(url, 0)
            time.sleep(0.1)
        for i in range(total[1]):
            url = self.url_temp[1].format(i + 1)
            self.get_content_list(url, 1)
            time.sleep(0.1)


class HuaNengSpider(BaseSpider):
    """
    华能集团
    http://ec.chng.com.cn/ecmall/more.do?start=0
    http://ec.chng.com.cn/ecmall/morelogin.do?type=107&start=0
    """
    def __init__(self):
        super(HuaNengSpider, self).__init__()

        self.url_temp_list = ["http://ec.chng.com.cn/ecmall/morelogin.do?type=107&start={}",
                              "http://ec.chng.com.cn/ecmall/more.do?start={}"]
        self.url_part = "http://ec.chng.com.cn/ecmall/announcement/announcementDetail.do?announcementId={}"
        self.map_dict = {0: "询价公告", 1: "通知公告"}
        self.filename = "huaneng_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['来源', '名称', '开始时间', '链接'])
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
                print(item)
                write_list = [item["src"], item["title"], item["date"], item["href"]]
                self.write_file(write_list, self.filename)

    def run(self):
        total_list = self.get_total()
        i = 0
        while i < total_list[0]:
            url = self.url_temp_list[0].format(i)
            self.get_content(url, 0)
            i += 10
            time.sleep(0.1)
        j = 0
        while j < total_list[1]:
            url = self.url_temp_list[1].format(j)
            self.get_content(url, 1)
            j += 10
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
        writer.writerow(['来源', '编号', '名称', '开始时间', '链接'])
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
                item["num"] = cont.xpath(".//a/span/text()")[0] if cont.xpath(".//a/span/text()") else ""
                # item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"] = cont.xpath("./span/text()")[0].strip()
                href_str = cont.xpath(".//a[1]/@href")[0]
                item["href"] = self.url_part + href_str
                print(item)
                write_list = [item["src"], item["num"], item["title"], item["date"], item["href"]]
                self.write_file(write_list, self.filename)

    def run(self):
        total_list = self.get_total()
        for i, total in enumerate(total_list):
            j = 1
            while j < total+1:
                url = self.url_temp_list[i].format(j)
                print(url)
                self.get_content(url, i)
                j += 1
                time.sleep(0.1)


class ZhaoCaiSpider(BaseSpider):
    """
    招标与采购网
    https://www.zbytb.com/gongcheng-1.html
    """
    def __init__(self):
        super(ZhaoCaiSpider, self).__init__()
        self.url_temp_list = ["https://www.zbytb.com/gongcheng-{}.html",
                              "https://www.zbytb.com/huowu-{}.html",
                              "https://www.zbytb.com/fuwu-{}.html",
                              "https://www.zbytb.com/dianli-{}.html",
                              "https://www.zbytb.com/shiyou-{}.html"]
        self.url_part = ""
        self.map_dict = {0: "工程", 1: "货物", 2: "服务", 3: "电力", 4: "石油"}
        self.filename = "zhaocai_list.csv"
        f = codecs.open(self.filename, 'w', 'utf_8_sig')
        writer = csv.writer(f)
        writer.writerow(['来源', '地区', '名称', '开始时间', '链接'])
        f.close()

    def get_total(self):
        total_list = []
        for url in self.url_temp_list:
            url = url.format(1)
            detail_html_str = self.parse_url(url)
            detail_html = etree.HTML(detail_html_str)
            total_str = detail_html.xpath('//div[@class="pages"]//cite/text()')[0]
            total_num = int(re.findall(r"条/(.*?)页", total_str)[0])
            total_list.append(total_num)
        return total_list

    def get_content(self, detail_url, num):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            # print(detail_html_str)
            detail_html = etree.HTML(detail_html_str)
            cont_list = detail_html.xpath('//tr[@class="hover_tr"]')
            for cont in cont_list:
                item = {}
                item["src"] = self.map_dict[num]
                item["title"] = cont.xpath("./td[2]/a/text()")[0]
                item["area"] = cont.xpath("./td[1]/a/text()")[0]
                # item["state"] = cont.xpath("./td[1]/span/text()")[0]
                item["date"] = cont.xpath("./td[4]/text()")[0].strip()
                item["href"] = cont.xpath("./td[2]/a/@href")[0].strip()
                print(item)
                write_list = [item["src"], item["area"], item["title"], item["date"], item["href"]]
                self.write_file(write_list, self.filename)

    def run(self):
        total_list = self.get_total()
        for i, total in enumerate(total_list):
            j = 1
            while j < total+1:
                url = self.url_temp_list[i].format(j)
                print(url)
                self.get_content(url, i)
                j += 1
                time.sleep(1)


if __name__ == '__main__':
    try:
        guodian=GuoDianSpider()
        guodian.run()
    except:
        print("guodian run error...")
        traceback.print_exc()
    try:
        guoneng=GuoNengSpider()
        guoneng.run()
    except:
        print("guoneng run error...")
        traceback.print_exc()
    try:
        huadian=HuaDianSpider()
        huadian.run()
    except:
        print("huadian run error...")
        traceback.print_exc()
    try:
        huaneng=HuaNengSpider()
        huaneng.run()
    except:
        print("huaneng run error...")
        traceback.print_exc()
    try:
        shenhua=ShenHuaSpider()
        shenhua.run()
    except:
        print("shenhua run error...")
        traceback.print_exc()
    # try:
    #     zhaocai=ZhaoCaiSpider()
    #     zhaocai.run()
    # except:
    #     print("zhaocai run error...")
    #     traceback.print_exc()
