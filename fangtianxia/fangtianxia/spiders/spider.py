# -*- coding: utf-8 -*-
import scrapy
import hashlib
from urllib import parse
from fangtianxia.items import FangtianxiaItem

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    url = 'https://alaer.esf.fang.com/newsecond/esfcities.aspx'

    def get_md5(self, url):
        if isinstance(url, str):
            url = url.encode("utf-8")
        m = hashlib.md5()
        m.update(url)
        return m.hexdigest()

    def start_requests(self):
        yield scrapy.Request(url=self.url,
                             dont_filter=True,
                             )

    def parse(self, response):
        # citylist = response.css("div.onCont ul li a::attr(href)").extract()
        # cityname = response.css("div.onCont ul li a::text").extract()
        # # citylist = set(citylist)
        # # cityinformation = response.xpath("//div[@class='onCont']/ul/li/a/text()|//div[@class='onCont']/ul/li/a/@href").extract()
        # for url, name in zip(citylist, cityname):
        #     url = parse.urljoin(response.url, url)
        #     url = parse.urljoin(url, '/housing/')
        #     # url = "https://abazhou.esf.fang.com/housing/"
        #     yield scrapy.Request(url=url,
        #                          dont_filter=True,
        #                          meta={
        #                              'cityname': name,
        #                          },
        #                          callback=self.analysis_page)
        yield scrapy.Request(url='https://esf.fang.com/housing/',
                             dont_filter=True,
                             meta={
                                 'cityname': '北京',
                             },
                             callback=self.analysis)
    def analysis(self, response):
        pagelist = response.css("div.sq-info a::attr(href)").extract()
        for page in pagelist:
            yield scrapy.Request(url=parse.urljoin(response.url, page),
                                 dont_filter=True,
                                 meta={
                                     'cityname': response.meta['cityname'],
                                 },
                                 callback=self.analysis_page,
                                 )

    def analysis_page(self, response):
        houselist = response.css("div.houseList div.list.rel.mousediv dd p a.plotTit::attr(href)").extract()
        for houseurl in houselist:
            if 'com' in houseurl:
                yield scrapy.Request(url='http:' + houseurl.replace("jiage/", ''),
                                     dont_filter=True,
                                     meta={
                                         'cityname': response.meta['cityname'],
                                     },
                                     callback=self.get_price,
                                     )
        next_url = response.css("#PageControl1_hlk_next::attr(href)").extract_first()
        if next_url == None:
            pass
        else:
            print(next_url)
            next_url = parse.urljoin(response.url, next_url)
            yield scrapy.Request(url=next_url,
                                 dont_filter=True,
                                 meta={
                                     'cityname': response.meta['cityname'],
                                 },
                                 callback=self.analysis_page)

    def get_price(self, response):
        price = response.css('span.prib::text').extract_first()
        url = parse.urljoin(response.url, '/xiangqing/')
        yield scrapy.Request(url=url,
                             dont_filter=True,
                             meta={
                                'price': price,
                                'cityname': response.meta['cityname'],
                             },
                             callback=self.get_information)

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        except TypeError:
            return False

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    def get_information(self, response):
        item = FangtianxiaItem()
        url = response.url
        url_hash = self.get_md5(url=url)
        oldprice = response.meta['price']
        nowprice = response.css("span.red::text").extract_first()
        title = response.css("a.tt::text").extract_first()
        city = response.meta['cityname']
        if nowprice == None:
            information = response.xpath("//div[@class='con_left']/div[1]/div[2]/dl/dd")
        else:
            information = response.xpath("//div[@class='con_left']/div[2]/div[2]/dl/dd")
        if information:
            xiaoqudizhi = ''
            lvhualv = ''
            wuyegongsi = ''
            jianzhujiegou = ''
            rongjilv = ''
            youbian = ''
            loudong = ''
            wuyefei = ''
            jianzhuniandai = ''
            kaifashang = ''
            jianzhumianji = ''
            fangwuzongshu = ''
            wuyeleibie = ''
            fujiaxinxi = ''
            zhandimianji = ''
            jianzhuleixing = ''
            chanquanmiansu = ''
            suoshuquyu = ''
            if oldprice == None or self.is_number(oldprice):
                oldprice = 0
            if nowprice == None or self.is_number(nowprice):
                nowprice = 0
            if title == None:
                title = ''
            for infor in information:
                name = infor.css("dd strong::text").extract_first()
                text = infor.css("dd::text").extract_first()
                if text == None:
                    text = infor.css("dd span::text").extract_first()
                if '小区地址' in name:
                    xiaoqudizhi = text
                elif '绿' in name:
                    lvhualv = text
                elif '物业公司' in name:
                    wuyegongsi = text
                elif '结构' in name:
                    jianzhujiegou = text
                elif '容' in name:
                    rongjilv = text
                elif '邮' in name:
                    youbian = text
                elif '楼栋总数' in name:
                    loudong = text
                elif '物 业 费' in name:
                    wuyefei = text
                elif '建筑年代' in name:
                    jianzhuniandai = text
                elif '发' in name:
                    kaifashang = text
                elif '建筑面积' in name:
                    jianzhumianji = text
                elif '房屋总数' in name:
                    fangwuzongshu = text
                elif '物业类别' in name:
                    wuyeleibie = text
                elif '附加信息' in name:
                    fujiaxinxi = text
                elif '占地面积' in name:
                    zhandimianji = text
                elif '建筑类型' in name:
                    jianzhuleixing = text
                elif '产权描述' in name:
                    chanquanmiansu = text
                elif '所属区域' in name:
                    suoshuquyu = text
                else:
                    print(name)
            item['city'] = city
            item['title'] = title
            item['url'] = url
            item['url_hash'] = url_hash
            item['oldprice'] = oldprice
            item['nowprice'] = nowprice
            item['xiaoqudizhi'] = xiaoqudizhi
            item['lvhualv'] = lvhualv
            item['wuyegongsi'] = wuyegongsi
            item['jianzhujiegou'] = jianzhujiegou
            item['rongjilv'] = rongjilv
            item['youbian'] = youbian
            item['loudong'] = loudong
            item['wuyefei'] = wuyefei
            item['jianzhuniandai'] = jianzhuniandai
            item['kaifashang'] = kaifashang
            item['jianzhumianji'] = jianzhumianji
            item['fangwuzongshu'] = fangwuzongshu
            item['wuyeleibie'] = wuyeleibie
            item['fujiaxinxi'] = fujiaxinxi
            item['zhandimianji'] = zhandimianji
            item['jianzhuleixing'] = jianzhuleixing
            item['chanquanmiansu'] = chanquanmiansu
            item['suoshuquyu'] = suoshuquyu
            yield item

