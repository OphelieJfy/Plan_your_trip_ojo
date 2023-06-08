### Import useful libraries 

# to easily manipulate operating systems
import os

# for logs manipulation 
import logging

# Import scrapy and scrapy.crawler 
import scrapy
from scrapy.crawler import CrawlerProcess


class BookingSpider(scrapy.Spider):

    # Name of your Spider
    name = "booking"

    # Url to start your spider from 
    start_urls = [
        'https://www.booking.com/'
    ]

    # Callback function that will be called when starting your spider
    def parse(self, response):
        return scrapy.FormRequest.from_response(
             response,
             formdata = {'ss':'paris'},
             callback = self.after_search
        )
        
    def after_search(self, response):

        accesses = response.xpath("//h3[@class='a4225678b2']")

        for access in accesses:
            
            yield {
                'name': access.xpath(".//div[contains(@class, 'fcab3ed991 a23c043802')]/text()").get(),
                'url': access.xpath(".//@href").get(),
                'offset': access.xpath("div[4]/div[2]/div/div/span/text()").get(),
            }
        
        try:
            offset = access.xpath("div[4]/div[2]/div/div/span/text()").get()
            offset2 = offset.split(' ')[1]
            next_page = response.request.url + "&offset=" + offset2
        except KeyError:
            # In the last page, there won't be any "href" and a KeyError will be raised
            logging.info('No next page. Terminating crawling process.')
        else:
            # If a next page is found, execute the parse method once again
            yield response.follow(next_page, callback=self.after_search)

# Name of the file where the results will be saved
filename = "booking_paris.json"

# If file already exists, delete it before crawling (because Scrapy will 
# concatenate the last and new results otherwise)
if filename in os.listdir('./'):
        os.remove('./' + filename)

# Declare a new CrawlerProcess with some settings

process = CrawlerProcess(settings = {
    'USER_AGENT': 'Firefox/111.0.',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        './' + filename : {"format": "json"},
    }
})

# Start the crawling using the spider you defined above
process.crawl(BookingSpider)
process.start()