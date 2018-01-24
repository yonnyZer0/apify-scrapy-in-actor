# -*- coding: utf-8 -*-
from scrapy import Request

from companiesprofiles.spiders.BaseSpider import BaseCrawlSpider

class ForresterSpider(BaseCrawlSpider):
    name = "forrester"
    allowed_domains = ["forrester.com"]
    start_urls = (
        'https://www.forrester.com/hub/analysts.xhtml',
    )

    test_mode = False
    # test_profile_url = "https://www.forrester.com/J.%20P.%20Gownder"
    test_profile_url = "https://www.forrester.com/Julie%20A.%20Ask"
    # test_profile_url = "https://www.forrester.com/J.-P.-Gownder"

    company = "Forrester"
    company_url = "https://www.forrester.com/"

    xpaths = {
            "profiles": {"xpath": "//ul[@class='analyst-listing']/li/a/@href"},

            "bio_education": {
                "xpath": "//div[contains (., 'Education')]/following-sibling::p[1]"
            },
            "biography": {
                "xpath": "//div[@class=\"toggle_cls\"]/p[1]"
            },
            "linkedin": {
                "xpath": "//a[contains(@href,'linkedin.com')]/@href"
            },
            "name_first": {
                "regex": "^(.+?) ",
                "xpath": "//div[@class=\"analyst-contents flowleft analyst-title\"]/h2/descendant-or-self::text()"
            },
            "name_full": {
                "xpath": "//div[@class=\"analyst-contents flowleft analyst-title\"]/h2/descendant-or-self::text()"
            },
            "name_second": {
                "regex": "[^ ]*$",
                "xpath": "//div[@class=\"analyst-contents flowleft analyst-title\"]/h2/descendant-or-self::text()"
            },
            "photo_url": {
                "xpath": "//div[@class=\"analyst-image flowleft\"]/img"
            },
            "previous_bio": {
                "xpath": "//div[contains (., 'Previous Work Experience')]/following-sibling::p[1]"
            },
            "taxonomy_industry": {
                "regex": "^(.+?)PROFESSIONALS",
                "xpath": "//div[@class=\"analyst-contents flowleft analyst-title\"]/h3/span[@class=\"bold\"]"
            },
            "taxonomy_topics": {
                "xpath": "//h2[contains (., 'Research Coverage')]/following-sibling::div["
                         "@class=\"customer_links\"]/a",
                "sub_xpath": "./descendant-or-self::text()",
            },
            "title": {
                "regex": "^(.+?)serving",
                "xpath": "//div[@class=\"analyst-contents flowleft analyst-title\"]/h3"
            },
            "twitter": {
                "regex": "[^/@]+$",
                "xpath": "//a[contains (@href, 'twitter.com')]/@href"
            },
            "url_blog": {
                "xpath": "(//a[contains (@href, 'blogs.forrester.com')]/@href)[1]"
            }
        }

    def parse_profiles(self, response):
        profiles = response.xpath(self.xpaths.get('profiles').get('xpath')).extract()
        for profile_url in profiles:
            yield Request(url=self._make_complete_url(profile_url),
                          callback=self.parse_data_page_method)

        alphabets = response.xpath('//a[@class="analyst-alphabets"]/@href').extract()
        for alpha in alphabets:
            yield Request(url=self._make_complete_url(alpha),
                          callback=self.parse_profiles)
