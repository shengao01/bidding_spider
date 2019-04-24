import requests
import csv
import codecs
from lxml import etree
import json
import time
import re


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
        self.url_temp_list = ["http://www.cgdcbidding.com/ggsb/index_{}.jhtml", "http://www.cgdcbidding.com/gggc/index_{}.jhtml", "http://www.cgdcbidding.com/ggjg/index_{}.jhtml"]
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

    def get_url_list(self, total):
        # url_list = [self.url_temp.format(i) for i in range(1, 2)]
        url_list = [self.url_temp.format(i) for i in range(1, total+1)]
        print(url_list)
        return url_list

    def get_content_list(self, detail_url):
        if detail_url is not None:
            detail_html_str = self.parse_url(detail_url)
            dict_str = detail_html_str[2:-1]
            item_dict = json.loads(dict_str)
            item_list = item_dict["data"]["rows"]
            for row in item_list:
                write_list = [row["inquireName"], row['inquireCode'], row['publishArea'], row['publishTimeString'], row['quotDeadlineString'], row['articleUrl']]
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
        url_list = self.get_url_list(total)
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
        self.url_temp = ["https://www.chdtp.com.cn/webs/displayNewsCgxxAction.action?page.currentpage={}", "https://www.chdtp.com.cn/webs/queryWebZbgg.action?page.currentpage={}"]
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


"""
华能集团
http://ec.chng.com.cn/ecmall/more.do?start=20
http://ec.chng.com.cn/ecmall/morelogin.do?type=107&start=20
神华集团
http://www.shenhuabidding.com.cn/bidweb/001/001002/001002001/1.html
招标与采购网
https://www.zbytb.com/gongcheng-1.html
"""


if __name__ == '__main__':
    guodian = GuoDianSpider()
    guoneng = GuoNengSpider()
    huadian = HuaDianSpider()
    # guodian.run()
    # guoneng.run()
    huadian.run()

