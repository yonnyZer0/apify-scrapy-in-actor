# -*- coding: utf-8 -*-
import logging
import re
from companiesprofiles.spiders.BaseSpider import BaseCrawlSpider
from scrapy import Selector
class MercatorSpider(BaseCrawlSpider):
    name = "mercator"
    allowed_domains = ["mercatoradvisorygroup.com"]
    start_urls = (
        'https://www.mercatoradvisorygroup.com/About/Team/',
    )

    company = "Mercator Advisory Group"
    company_url = "https://www.mercatoradvisorygroup.com"

    test_mode = True
    # test_profile_url = "https://www.mercatoradvisorygroup.com/Analysts/Raymond_Pucci/"
    test_profile_url = "https://www.mercatoradvisorygroup.com/Analysts/Karen_Augustine/"
    # test_profile_url = "https://www.mercatoradvisorygroup.com/Analysts/Brian_Riley/"
    test_profile_url = "https://www.mercatoradvisorygroup.com/Analysts/Steve_Murphy/"

    xpaths = {
                "profiles": {"xpath": "//div[@class='team-cell']/a/@href"},

                "bio_education": {
                    "xpath": "//strong[contains (., 'Education')]"
                             "/following-sibling::text()[position()=1 and not(parent::strong)]"
                },
                "bio_blurb": {
                    "xpath": "//strong[contains (., 'Roles and Responsibilities')]"
                             "/following::text()"
                },

                # "biography": {
                #     # "xpath": "//div[@class=\"text divBio\"]/p/node()[not(self::div)]"
                # },
                "contact_email": {
                    "xpath": "//text()[contains (., 'Email:')]/following-sibling::a[contains ("
                             "@href, 'mailto:')]"
                },
                "contact_phone": {
                    "xpath": "//text()[contains (., 'Email:')]/following-sibling::text()"
                },
                "name_full": {
                    "xpath": "//div[@id=\"analyst-profile-info\"]/h2"
                },
                "photo_url": {
                    "xpath": ".//img[not(@style)][@id=\"ctl00_ctl00_pMainBody_pContent_AnalystHeadshot\"][contains(concat(' ',normalize-space(@class),' '),\" analyst-profile-headshot \")]"
                },

                "previous_bio": {
                    "xpath": "//div[@id='ctl00_ctl00_pMainBody_pContent_AnalystBioDiv']/p",
                },
                "previous_positions": {
                    "xpath": "//div[@id='ctl00_ctl00_pMainBody_pContent_AnalystBioDiv']/p",
                },
                "title": {
                    "xpath": "//div[@id=\"analyst-profile-info\"]/h3/descendant-or-self::text()"
                }
            }

    paragraph_item_keys = ["biography", "bio_education", "bio_personal", "previous_bio",
                           "previous_positions"]

    def _clean_paragraph_single_lines(self, paragraph_html, key):
        if key == "previous_bio":
            paragraph_html = paragraph_html.replace('<br></strong>', '</strong>')
            sel = Selector(text=paragraph_html)
            previous_experience_strong_text = sel.xpath('//strong[contains(text(), '
                                                           '"Previous Experience")]'
                                                           '/text()').extract_first()

            if previous_experience_strong_text:
                paragraph_strong_header_text = '<strong>%s</strong>' % previous_experience_strong_text
                after_previous_experience = paragraph_html.split(paragraph_strong_header_text)

                if len(after_previous_experience) == 2:
                    just_after_previous_experience = after_previous_experience[1].split('<strong>')
                    paragraph_html = just_after_previous_experience[0]
            else:
                paragraph_html = ""


        if key == "previous_positions":
            paragraph_html = paragraph_html.replace('<br></strong>', '</strong>')
            after_previous_experience = paragraph_html.split('<strong>Professional Background</strong>')
            if len(after_previous_experience) == 2:
                just_after_previous_experience = after_previous_experience[1].split('<strong>')
                return just_after_previous_experience[0]
            else:
                return ""

        paragraph_html = super(MercatorSpider, self)._clean_paragraph_single_lines(
            paragraph_html,key)

        return paragraph_html
