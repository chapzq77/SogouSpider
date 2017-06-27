# -*- coding: utf-8 -*-

import scrapy


class SogouspiderItem(scrapy.Item):
    # 输入人名返回的title
    title = scrapy.Field()
    # 返回的content
    content = scrapy.Field()
    # title中的url
    url = scrapy.Field()
    # 查询的词
    word = scrapy.Field()
