import scrapy
from ..items import CodingTestItem
from scrapy import Selector
import requests

class ExampleSpider(scrapy.Spider):
    name = 'example'
    start_urls = ['https://contest-646508-5umjfyjn4a-ue.a.run.app/listing'] # Provide the link
    url_list = []
    def parse(self, response):
        products_list = []
        response_html = response.text
        # make html file to look
        # makeHTML(response, "main.html")
        product_objs = response.xpath('//div[@class="item"]//a').extract()  #xpath for products from html
        next_page_url = ""
        for product in product_objs:            #iterate over each product
            if("next" not in product.lower() and "previous" not in product.lower()):
                self.count = self.count+1
                product_selector = Selector(text=product)
                product_link = product_selector.xpath("//a").xpath("@href").get()
                product_url = response.urljoin(product_link)
                response_html = response_html.replace(product,"")               # remove data from html once visuted
                yield scrapy.Request(url = product_url, callback = self.parse_item)
            elif("next page" in product.lower()):
                product_data = product_selector = Selector(text=product)
                next_page_url = product_data.xpath("//a").xpath("@href").get()

        if(next_page_url):
            probable_next_page_urls = Selector(text=response_html).xpath("//a").extract()
            next_page_url = response.urljoin(next_page_url)
                    # break
            if(next_page_url):
                yield scrapy.Request(url = next_page_url, callback = self.parse)

    def parse_item(self,response):
        item_obj = CodingTestItem()
        flavor = ""
        item_name = response.xpath("//div[@id='2']//h2//text()").extract_first()  #Parse name
        item_id = response.xpath("//span[@id='uuid']//text()").extract_first()               # parse id
        flavor_text_list = response.xpath("//div[@id='2']//p").extract()
        for flavor_item in flavor_text_list:
            if("flavor:" in flavor_item.lower()):
                flavor = Selector(text=flavor_item).xpath("//span//text()").get()
                if(flavor == "NO FLAVOR" or flavor == ""):                                                    # get api call if needed
                    flavor_link = Selector(text=flavor_item).xpath("//span").xpath("@data-flavor").get()
                    flavor = requests.get(response.urljoin(flavor_link)).json()["value"]
        image_id = None
        try:
            full_html = response.text
            image_id_list = Selector(text=full_html).xpath("//div[@id='2']//img").xpath("@src").extract()
            if(len(image_id_list)==0):
                pattern = r'version=\s*(\{.*?\})\s*\n'
                json_data = response.css('script::text').extract()
                for data in json_data:
                    if("mainimage" in data):
                        for line in data.split("\n"):
                            if("const iid" in line):
                                image_id = line.split("=")[1].strip().remove('\'',"")
                                break
                if not image_id:
                    image_id = None
            else:
                image_id = image_id_list[0].split("/")[2].split(".")[0]
                # print(json_data) 
        item_obj["item_id"] = item_id
        item_obj["image_id"] = image_id
        item_obj["name"] = item_name 
        item_obj["flavor"] = flavor
        yield item_obj

        recommandation_html = response.xpath("//div[@id='3']//a").extract()           # page in recommendation
        for recommendation in recommandation_html:
            recommenation_link=Selector(text=recommendation).xpath("//a").xpath("@href").get()
            yield scrapy.Request(url=response.urljoin(recommenation_link),callback = self.parse_item)


# def makeHTML(response,file_name):
#     with open(file_name,"w+",encoding="utf-8") as fp:
#         fp.write(response.text)