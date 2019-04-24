# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy

class GuonengSpider(scrapy.Spider):
    name = 'guoneng'
    allowed_domains = ['www.shenhuabidding.com.cn']
    start_urls = ['http://www.shenhuabidding.com.cn/']

    def parse(self, response):
        item = {}
        title_list = response.xpath('//div[@class="right-bd"]/ul[@class="right-items"]/li')
        for li in title_list:
            item["bianhao"] = li.xpath("./div/a[1]/span/text()").extract_first()
            item["title"] = li.xpath("./div/a[1]/@title").extract_first()
            item["date"] = li.xpath("./span[@class="r"]/text()").extract_first()
            href = li.xpath("./div/a[1]/@href").extract_first()
            item["href"] = "http://www.shenhuabidding.com.cn" + href
