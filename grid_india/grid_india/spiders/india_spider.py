import scrapy

class GridSpider(scrapy.Spider):
    name = 'grid_spider'
    allowed_domains = ['report.grid-india.in']
    start_urls = ['https://report.grid-india.in/psp_report.php']

    def parse(self, response):
        for year in range(2014, 2025):
            yield scrapy.FormRequest(
                url='https://report.grid-india.in/psp_report.php',
                formdata={'selected_date': f'{year}-01-01'},
                callback=self.parse_report_page,
                meta={'year': year}
            )

    def parse_report_page(self, response):
        base_url = 'https://report.grid-india.in'
        year = response.meta['year']
        for link in response.xpath('//a[contains(@href, ".pdf")]/@href').extract():
            pdf_url = base_url + link[1:]
            yield scrapy.Request(
                url=pdf_url,
                callback=self.save_pdf,
                meta={'pdf_url': pdf_url, 'year':year}
            )
            
    def save_pdf(self, response):
        pdf_url = response.meta['pdf_url']
        year = response.meta['year']
        yield {
            'year':year,
            'pdf_url': pdf_url,
            'pdf_content': response.body
        }