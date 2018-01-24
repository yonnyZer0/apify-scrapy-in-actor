import logging
from companiesprofiles.spiders.BaseSpider import BaseCrawlSpider

class ParksAssociatesSpider(BaseCrawlSpider):
    name = "parks_associates"
    allowed_domains = ["parksassociates.com"]
    start_urls = (
        'http://www.parksassociates.com/meet-the-team',
    )

    company = "parksassociates"
    company_url = "http://www.parksassociates.com"
    multiple_items_per_page = True
    test_mode = False
    # test_profile_url = ""

    xpaths = {
      "profiles": {"xpath": "//div[@class='team']/ul/li[not(@class='dept')]"},
 
      "biography": {
            "xpath": ".//div[@class=\"bio\"]/p"
      }, 
      "contact_email": {
            "regex": "(?<=mailto:).*", 
            "xpath": ".//div[@class=\"bio\"]/h3/a[contains (@href, 'mailto:')]/@href"
      }, 
      "name_full": {
            "xpath": ".//div[@class=\"bio\"]/h3/a"
      }, 
      "photo_url": {
            "xpath": ".//img"
      }, 
      "title": {
            "regex": "[^,].*$", 
            "xpath": ".//div[@class=\"bio\"]/h3/a/following-sibling::text()"
      }, 
      "twitter": {
            "regex": "[^/@]*$", 
            "xpath": ".//div[@class=\"bio\"]/a[contains (@href , 'twitter')]/@href"
      }
}
    def _do_parse_profile(self, profile):
        profile_body = profile.get('body')
        if profile_body:
            text = 'Parks Associates</a>, About Parks Associates</h3>'
            if text in profile_body:
                logging.info("ignoring first profile.")
                return False
        return True