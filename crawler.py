from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.log import configure_logging
import time
import sys, os
import argparse
import logging

#now = datetime.datetime.now()
datecrwl = (time.strftime("%d%m%Y"))

parser = argparse.ArgumentParser(description='Web crawler for DFIR.')
parser.add_argument('-s','--spoofed', help='Spoofd domain to be analyzed', required=True)
parser.add_argument('-u','--urlsfile', help='File with URLs to analyze', required=True, default='')
args = parser.parse_args()
argsdict = vars(args)
domain = argsdict['spoofed']

urllist = argsdict['urlsfile']
if len(urllist) > 0:
    with open(urllist, 'r') as f:
        urls = f.readlines()
else:
    urls = ['https://' + domain]

logging.warning("\nStarting analysis on "+domain)

folder = domain + '_' + datecrwl
if not os.path.exists('./' + folder):
        os.makedirs('./' + folder)
if not os.path.exists('./' + folder + '/images'):
        os.makedirs('./' + folder + '/images')

class WebSpider(CrawlSpider):
    name = 'spoofPage'
    allowed_domains = [domain]
    start_urls = urls
    user_agent ='Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'
    rules = (
#        Rule(LinkExtractor(), callback='parse_item', follow=True),
        Rule(LinkExtractor(), callback='parse_item'),
     )

    def parse_item(self, response):
        filename = response.url.split("/")[-1].split("?")[0]
        image_urls=[]
        with open('./' + folder + '/' +filename, 'wb') as f:
            f.write(response.body)
        for image in response.xpath('//img/@src').extract():
            image_urls.append(response.urljoin(image))
        yield {'url': response.url,
            'referer': response.request.headers.get('Referer'),
            'response_headers': response.headers,
            'images_data':image_urls
               }

def run():

    configure_logging()
    runner = CrawlerRunner({
        'FEED_FORMAT': 'json',
        'FEED_URI': folder + '.json',
    })
    runner.crawl(WebSpider)

    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()  # the script will block here until all crawling jobs are finished


if __name__ == '__main__':   
    run()
    logging.warning("\nAnalysis finished for domain "+domain)

