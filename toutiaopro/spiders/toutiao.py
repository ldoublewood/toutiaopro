import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from toutiaopro.items import ToutiaoproItem
from time import sleep
from scrapy.http import HtmlResponse
import logging
class ToutiaoSpider(scrapy.Spider):
    name = 'toutiao'
    #data = input("请输入要爬取的关键字:")
    #number = int(input("请输入要爬取的数量:"))  # 控制爬取数量
    number = 4
    #address = 'https://www.toutiao.com/search/?keyword='+data
    address = 'https://www.toutiao.com/c/user/token/MS4wLjABAAAAAGsDYNOXFdmGdHtu3iD0wyiybaPhzDbyIfpAC-nFb4w'
    start_urls = [address]
    urls = []
    num = 0 #控制浏览器下滑循环次数
    index = 0 #控制收集连接条数


    #初始化浏览器
    def __init__(self):
        CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
        WINDOW_SIZE = "1920,1080"
        service = Service(executable_path=CHROMEDRIVER_PATH)
        #根据自己的chrome驱动路径设置
        chrome_options = Options()
        chrome_options = webdriver.ChromeOptions()
#        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
        chrome_options.add_argument('--no-sandbox')

        self.bro1 = webdriver.Chrome(service=service, options=chrome_options)
        self.bro2 = webdriver.Chrome(service=service, options=chrome_options)


    #获取到关键字的文章列表
    def parse(self, response):

        self.artical_list(response)


        #控制爬取数量
        while self.index<=self.number:
            # for href in self.urls:
            #     yield scrapy.Request(href, callback=self.parse_model)
            index = self.index
            yield scrapy.Request(self.urls[index], callback=self.parse_model)

            #获取10篇文章后刷新文章列表
            #有些关键字一页若没有这个数，则需调低阈值
            if self.num == 5:
                #滑动滚动条
                self.bro1.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                sleep(5)
                page_text = self.bro1.page_source
                print("if里面")
                #print(page_text)

                new_response = HtmlResponse(url='',body=page_text,encoding='utf-8', request='')
                # self.artical_list(page_text)
                self.artical_list(new_response)
                self.num = 0
                self.index = self.index + 1
                print("if中的index", self.index)
            else:
                print("else里面",self.num)
                self.index = self.index + 1
                print("else中的index",self.index)
                self.num = self.num + 1
    #文章解析
    def parse_model(self,response):

        title = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/h1/text()').extract_first()
        content = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/article//text()').extract()
        content = ''.join(content)
        span = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span')
        if len(span) == 2:
            author = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[1]/text()').extract_first()
            time = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[2]/text()').extract_first()
        else:
            author = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[2]/text()').extract_first()
            time = response.xpath('//*[@id="root"]/div/div[2]/div[1]/div[2]/div[1]/span[3]/text()').extract_first()

        #提交管道
        #self.bro1.excute_script('window.scrollTo(0, document.body.scrollHeight)')
        item = ToutiaoproItem()
        item['title'] = title
        item['content'] = content
        item['time'] = time
        item['author'] = author
        logging.log(logging.WARNING, item)
        yield item

    #列表解析
    def artical_list(self, response):
        # 获取到列表属性
        div_list = response.xpath('/html/body/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div')
        for div in div_list:
            urls_temp = div.xpath('./div/div/div[2]//a/@href').extract()
            url = list(filter(lambda x: x.startswith("https://www.toutiao.com"), urls_temp))[0]
            self.urls.append(url)
            logging.log(logging.WARNING,  "appending full url is:" + url)

        #div_list = new_response.xpath('/html/body/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div')
        #num_urls = len(self.urls)
        #num_div = len(div_list)
        #for div in range(num_urls,num_div):
        #    href_temp = div_list[div].xpath('./div/div/div/div/div//@href').extract_first()
        #    href_temp = 'https://www.toutiao.com/a'+href_temp.split('/',3)[2]
        #    self.urls.append(href_temp)
        #    print("!!!!!!!!!!!!!")
        #    print(href_temp)
        #    print("!!!!!!!!!!!!")


