# https://statusinvest.com.br/acoes/busca-avancada
import scrapy
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pathlib import Path


class seleniumSpider(scrapy.Spider):
    name = 'statusinvest'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
    start_urls = ['https://statusinvest.com.br/acoes/busca-avancada']

    def __init__(self):
        options = Options()
        options.headless = True
        exec_path = Path(__file__).parent / '../conf/geckodriver.exe'
        self.driver = webdriver.Firefox(options=options,
                                        executable_path=exec_path)

    def parse(self, response):
        self.driver.get(response.url)
        find = self.driver.find_element_by_xpath(
            '//button[@data-tooltip="Clique para fazer a busca com base nos valores informados"]')
        find.click()
        time.sleep(2)

        sel = scrapy.Selector(text=self.driver.page_source)

        for item in sel.xpath('//tr[@class="item"]'):
            print(item)
            yield {
                'text': item.xpath(
                    '//td[@data-key="ticker"]/@title').extract_first(),
                'pl': item.xpath(
                    '//td[@data-key="p_L"]/text()').extract_first(),
                'evebit': item.xpath(
                    '//td[@data-key="eV_Ebit"]/text()').extract_first(),
                'roe': item.xpath(
                    '//td[@data-key="roe"]/text()').extract_first(),
                'roic': item.xpath(
                    '//td[@data-key="roic"]/text()').extract_first(),
            }

        # yield scrapy.Request(self.driver.current_url, callback=self.parse2)
        self.driver.close()

    def parse2(self, response):
        print('you are here!')


# class LoginSpider(scrapy.Spider):
'''class LoginSpider(scrapy.Spider):
    name = "statusinvest"
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
    start_urls = ["https://statusinvest.com.br/acoes/busca-avancada"]

    def parse(self, response):
        scrapy.FormRequest.from_response(response,
                                         # formname="Form",
                                         clickdata={
                                             "data-tooltip": "Clique para fazer a busca com base nos valores informados"},
                                         callback=self.after_find)

        # print("##########" + response.text)

        for item in response.xpath('//tr[@class="item"]'):
            ticker = item.xpath(
                ".//td[@data-key='ticker']/@title").extract_first()
            pl = item.xpath(".//td[@data-key='p_L']/text()").extract_first()
            evebit = item.xpath(
                ".//td[@data-key='eV_Ebit']/text()").extract_first()
            roe = item.xpath(
                ".//td[@data-key='roe']/text()").extract_first()
            roic = item.xpath(
                ".//td[@data-key='roic']/text()").extract_first()
            yield {"ticker": ticker, "pl": pl, "evebit": evebit, "roe": roe, "roic": roic}

        next_page = response.xpath(
            ".//li[@class='next']/a/@href").extract_first()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def after_find(self, response):
        # check login succeed before going on
        if "HTTP 403" in response.text:
            self.logger.error("Não foi possivel realizar a busca !!")
            return


if __name__ == "__main__":
    LoginSpider().thirdForm()'''
