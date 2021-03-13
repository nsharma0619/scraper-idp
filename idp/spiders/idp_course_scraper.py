import scrapy
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess


class IdpCourseScraperSpider(scrapy.Spider):
    name = 'idp_course_scraper'
    allowed_domains = ['www.idp.com']
    # start_urls = ['https://www.idp.com/global/search/all-accounting/']

    def start_requests(self):
        yield scrapy.Request('https://www.idp.com/global/search/all-accounting/', self.parse, meta={'area_study' : 'accounting'})

    def parse(self, response):
        cards = response.xpath("//ul[@class='product__listing product__list']/li")
        area_study = response.request.meta['area_study']
        for card in cards:
            try:
                course_name = card.xpath(".//div[@class='prd_inner_cont']/h2/a/text()").get().strip('\n')
            except:
                course_name = None
            university_name = card.xpath(".//div[@class='prd_inner_cont']/h3/a/span[@class='uniname']/text()").get().strip('\n')

            right_content = card.xpath(".//div[@class='right-content']")
            score = right_content.xpath(".//div[@class='score']")
            try:
                course_fee = score.xpath(".//p/text()").getall()[1].replace('\xa0\n', ' ')
            except:
                course_fee = None
            course_link = card.xpath(".//div/div/a/@href").get()

            yield response.follow(url=course_link, callback=self.parse_course, meta={'area_study' : area_study,'course_name' : course_name,'university_name' : university_name,'course_fee' : course_fee,'course_link' : course_link})
        
        next_page = response.xpath("//li[@class='pagination-next']/a[@class='glyphicon glyphicon-chevron-right']/@href").get()
        if next_page:
            print('i am running')
            yield  response.follow(url = next_page, callback=self.parse, meta={'area_study' : 'accounting'})

    def parse_course(self, response):
        meta = response.request.meta
        header = response.xpath("//div[@class='institution_count']").get()

        table = response.xpath("//table[@class='table desktop price-table table-responsive']")
        table = table.xpath(".//td/text()").getall()
        str1 = ''.join(table)
        str1 = str1.replace(',', '')
        months_master = ('january','feb','march','april','may','june','july','august','september','october','november','december')
        month = [i for i in months_master if i in str1.casefold()]



        header = BeautifulSoup(header, 'html.parser')
        try:
            location = header.find(text='Location').findNext('p').text
        except:
            location = None
        try:
            duration = header.find(text='Duration').findNext('p').text.replace('\xa0',' ')
        except:
            duration = None
        try:
            entry_score = header.find(text='Entry score').findNext('p').text    
        except:
            entry_score = None
        try:
            course_qualification = header.find(text='Qualification').findNext('p').text
        except:
            course_qualification = None
        yield {
            'location':location,
            'duration':duration,
            'entry_score':entry_score,
            'course_qualification':course_qualification,
            'area_study' : meta['area_study'],
            'course_name' : meta['course_name'],
            'university_name' : meta['university_name'],
            'course_fee' : meta['course_fee'],
            'course_link' : meta['course_link'],
            'intakes' : month
        }
            
process = CrawlerProcess(settings={
    "FEEDS": {
        "items.csv": {"format": "csv"},
    },
})

process.crawl(IdpCourseScraperSpider)
process.start()

