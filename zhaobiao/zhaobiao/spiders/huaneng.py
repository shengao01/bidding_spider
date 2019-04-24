# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy import FormRequest
from copy import deepcopy


class HuanengSpider(scrapy.Spider):
    name = 'huaneng'
    allowed_domains = ['chng.com.cn']
    start_urls = ['http://ec.chng.com.cn/ecmall/more.do?type=101&limit=50&start=0']

    def parse(self, response):
        item = {}
        item_list = response.xpath('//ul[@class="main_r_con"]/li')
        for li in item_list:
            item["title"] = li.xpath("./a/@title").extract_first()
            item["date"] = li.xpath("./p/text()").extract_first()
            iid_str = li.xpath("./a/@href").extract_first()
            iid = re.findall(r"announcementClick\('(.*?)'", iid_str)[0]
            item["href"] = "http://ec.chng.com.cn/ecmall/announcement/announcementDetail.do?announcementId=" + str(iid)
            # print(item)
            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail,
                meta={"item": deepcopy(item)}
            )

    def parse_detail(self, response):
        item = response.meta["item"]
        contents = response.xpath("//div[@class='main_box']/div[4]/div/p")
        item["content"] = ""
        for content in contents:
            item["content"] += str("".join(content.xpath("./span//text()").extract())).strip().strip("\xa0")
        print(item)
