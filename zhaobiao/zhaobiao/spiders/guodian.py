# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
from scrapy import FormRequest


class GuodianSpider(scrapy.Spider):
    name = 'guodian'
    allowed_domains = ['www.cgdcbidding.com']
    start_urls = ['http://www.cgdcbidding.com/ggsb/index_1.jhtml',]

    def parse(self, response):
        info_li = response.xpath('//div[@class="listbox"]//li')
        print(str(len(info_li)) + "+++++++++++++++++++++++++++++++++++++")
        for li in info_li:
            item = {}
            item["title"] = li.xpath("./a/@title").extract_first()
            item["date"] = li.xpath('./a//font/text()').extract_first()
            item["status"] = li.xpath('./a//span[@class="lb-date"]//text()').extract_first()
            item["href"] = li.xpath("./a/@href").extract_first()
            print(item)
            # if item["href"]:
            #     yield scrapy.Request(
            #         item["href"],
            #         callback=self.parse_detail,
            #         meta={"item": deepcopy(item)}
            #     )


    # def parse_detail(self, response):
    #     item = response.meta["item"]
    #     p_list = response.xpath("//div[@class='WordSection1']//p")
    #     item["content"] = ""
    #     for p in p_list:
    #         content = p.xpath(".//span//text()").extract_first()
    #         item["content"] += content.strip().replace("\\xa0", "")
    #     print(item)
