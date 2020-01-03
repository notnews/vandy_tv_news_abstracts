# -*- coding: utf-8 -*-

import os
import re
import gzip

import scrapy

class VandyNewsSpider(scrapy.Spider):
    name = 'vandy_news'
    allowed_domains = ['tvnews.vanderbilt.edu']
    start_urls = ['https://tvnews.vanderbilt.edu/siteindex/']

    def save_gzip_file(self, response, filename):
        fn = filename + '.gz'
        with gzip.open(fn, 'wb') as f:
            f.write(response.body)
        self.log('Saved file {}'.format(fn) )

    def parse(self, response):
        if not os.path.exists('./html'):
            os.makedirs('./html')
        if not os.path.exists('./html/broadcasts'):
            os.makedirs('./html/broadcasts')
        if not os.path.exists('./html/programs'):
            os.makedirs('./html/programs')
        page = response.url.split("/")[-2]
        filename = './html/vandy-%s.html' % page
        self.save_gzip_file(response, filename)
        filter = getattr(self, 'filter', None)
        for href in response.xpath("//table[@class='broadcastindex']//td/a"):
            if filter:
                try:
                    month = href.attrib['href'].split('/')[-1]
                except:
                    month = 'all'
                m = re.match(filter, month)
                if m:
                    yield response.follow(href, self.parse_month_index, meta={'filter': filter})
            else:
                yield response.follow(href, self.parse_month_index)


    def parse_month_index(self, response):
        self.log('Month index URL %s (meta=%r)' % (response.url, response.meta))
        for i, href in enumerate(response.xpath("//li[@class='elist_segment']/a")):
            yield response.follow(href, self.parse_broadcast, meta={'list': 'evening'})
            #if i > 5:
            #    break
        for i, href in enumerate(response.xpath("//li[@class='slist_segment']/a")):
            yield response.follow(href, self.parse_broadcast, meta={'list': 'special'})
            #if i > 5:
            #    break

    def parse_broadcast(self, response):
        """
        date, broadcast_title, broadcast_duration, broadcast_abstract, reporter(s)"
        """
        self.log('Broadcast URL %s (meta=%r)' % (response.url, response.meta))
        flist = response.meta['list']
        if flist == 'evening':
            href = response.css('p.broadcast-info a::attr(href)').get()
            yield response.follow(href, self.parse_program)
        else:
            idx = int(response.url.split('/')[-1])
            item = {}
            arr = response.css('p.broadcast-info::text').get().split(' for ')
            item['program_title'] = arr[0].strip()
            item['program_duration'] = ''
            item['broadcast_time'] = ''
            item['date'] = arr[-1].strip()
            item['broadcast_title'] = response.css('h4.video-title::text').get().strip()
            texts = response.css('div.video-description *::text').getall()
            item['broadcast_abstract'] = ''.join([a.strip() for a in texts])
            item['broadcast_order'] = idx
            duration = response.xpath("//dl[@class='video-meta']/dt[.='Duration:']/following-sibling::dd/text()").extract()[0]
            reporters = response.xpath("//dl[@class='video-meta']/dt[.='Reporters:']/following-sibling::dd/text()").extract()
            item['broadcast_duration'] = duration
            item['broadcast_reporter(s)'] = ''.join([r for r in reporters if r != duration])
            filename = './html/broadcasts/{}.html'.format(idx)
            self.save_gzip_file(response, filename)
            yield item

    def parse_broadcast_evening(self, response):
        """
        date, broadcast_title, broadcast_duration, broadcast_abstract, reporter(s)"
        """
        self.log('Broadcast Evening URL %s (meta=%r)' % (response.url, response.meta))
        item = response.meta['program_data']
        idx = int(response.url.split('/')[-1])
        item['date'] = response.css('p.broadcast-info::text').get().split(' for ')[-1].strip()
        item['broadcast_title'] = response.css('h4.video-title::text').get().strip()
        texts = response.css('div.video-description *::text').getall()
        item['broadcast_abstract'] = ''.join([a.strip() for a in texts])
        item['broadcast_order'] = idx
        duration = response.xpath("//dl[@class='video-meta']/dt[.='Duration:']/following-sibling::dd/text()").get()
        if not duration:
            # FIXME: HTML format problem in https://tvnews.vanderbilt.edu/broadcasts/1140139
            duration = response.xpath("//dt[.='Duration:']/following-sibling::dd/text()").get()
        reporters = response.xpath("//dl[@class='video-meta']/dt[.='Reporter(s):']/following-sibling::dd/text()").extract()
        item['broadcast_duration'] = duration
        item['broadcast_reporter(s)'] = ''.join([r for r in reporters if r != duration])
        filename = './html/broadcasts/{}.html'.format(idx)
        self.save_gzip_file(response, filename)
        yield item

    def parse_program(self, response):
        """
        program_title, program_duration, broadcast_time, broadcast_order
        """
        self.log('Program URL %s (meta=%r)' % (response.url, response.meta))
        idx = int(response.url.split('/')[-1])
        filename = './html/programs/{}.html'.format(idx)
        self.save_gzip_file(response, filename)
        title = response.css('h4.program-headline::text').get()
        if title:
            title = title.strip().split(' for ')[0]
        duration = response.css('p.program-duration::text').get()
        m = re.match('This program is\s(.*)\slong', duration)
        if m:
            duration = m.group(1)
        ids = response.css('li.listing p.id em::text').getall()
        tss = response.css('li.listing p.timestamp::text').getall()
        hrefs = response.css('li.listing a::attr(href)').getall()
        for id, ts, href in zip(ids, tss, hrefs):
            ts = ts.strip().replace(' — ', '-')
            meta = {'program_data': {'program_title': title, 'program_duration': duration, 'broadcast_time': ts}}
            yield response.follow(href, self.parse_broadcast_evening, meta=meta, dont_filter=True)
