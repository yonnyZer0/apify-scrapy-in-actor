from companiesprofiles.spiders.BaseSpider import BaseCrawlSpider

class GartnerSpider(BaseCrawlSpider):
    name = "gartner"
    allowed_domains = ["gartner.com"]
    start_urls = (
        'http://www.gartner.com/analysts/coverage',
    )

    company = "Gartner"
    company_url = "http://www.gartner.com"

    #test_mode = True
    # test_profile_url = ""

    paragraph_item_keys = ["biography", "bio_education", "bio_personal", "previous_bio",
                           "bio_blurb", "previous_positions",
                           "experience_company", "experience_industry", "experience",
                           ]

    xpaths = {
      "profiles": {"xpath": "//a[@class=\"analystName\"]/@href"},
      "bio_blurb": {
            "xpath": "//h3[contains (., 'Roles and Responsibilities')]/following-sibling::p"
      }, 
      "bio_education": {
            "xpath": "//h4[contains (., 'Education')]/following-sibling::p"
      }, 
      "experience": {
            "xpath": "//div[@class=\"a-info\"]/p/text()[1]"
      }, 
      "experience_company": {
            "regex": "^(.+?),",
            "xpath": "//div[@class=\"a-info\"]/p/text()[1]"
      }, 
      "experience_industry": {
            "regex": "[^,]*$", 
            "xpath": "//div[@class=\"a-info\"]/p/text()[1]"
      }, 
      "languages": {
            "xpath": "//h4[contains (., 'Languages')]/following-sibling::p/text()"
      }, 
      "location": {
            "xpath": "//div[@class=\"a-info\"]/p/text()[2]"
      }, 
      "name_full": {
            "xpath": "//div[@class=\"a-info\"]/h2"
      }, 
      "photo_url": {
            "xpath": "//div[@class=\"overall\"]/img"
      }, 
      "previous_bio": {
            "xpath": "//h4[contains (., 'Previous Experience')]/following-sibling::p"
      }, 
      "previous_positions": {
            "xpath": "//h4[contains (., 'Professional Background')]/following-sibling::p"
      }, 
      "recognition": {
            "xpath": "//h4[contains (., 'Industry Awards/Accolades')]/following-sibling::p"
      }, 
      "taxonomy_topics": {
            "xpath": "//h4[contains (., 'Areas of Coverage')]/following-sibling::ul/li"
      }, 
      "title": {
            "xpath": "//div[@class=\"a-info\"]/h4"
      }
}
    def _clean_paragraph_single_lines(self, paragraph_html, key):
        paragraph_html = paragraph_html.replace(u'\xa0', ' ')
        paragraph_html = paragraph_html.replace('\r', '').replace('\n', '')
        paragraph_html_cleaned_br = (paragraph_html.replace("<br>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<br />", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<BR>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<BR />", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<br/>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<BR/>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY))
        paragraph_html_cleaned_br = paragraph_html_cleaned_br.replace('   ', '')
        return paragraph_html_cleaned_br

    def format_paragraphs_list(self, paragraphs):
        result = []
        for p in paragraphs:
            p = p.strip()
            p = p.replace('   ', ' ').replace('  ', ' ')
            result.append(p)
        return result
