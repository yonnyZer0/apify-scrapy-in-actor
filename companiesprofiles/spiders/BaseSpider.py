import logging
import ssl
import urlparse
import colorlog
import re
from datetime import datetime

from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider
from scrapy import Request, Selector

from companiesprofiles.config import FRMT
from companiesprofiles.items import ProfileItem

from companiesprofiles.settings import *

__author__ = 'seni'

env = os.getenv('SCRAPY_ENV')

class BaseCrawlSpider(CrawlSpider):
    first_part = ''
    add_www = True
    xpaths = {
        'canonical_url': {'xpath': '//head/link[@rel="canonical"]/@href'},
        'page_title': {'xpath': '//head/title/text()'},
    }
    paragraph_item_keys = ["biography", "bio_education", "bio_personal", "previous_bio",
                           "bio_blurb", "previous_positions"]

    parse_profiles_from_index = True

    test_mode = False
    test_profile_url = None
    debug_xpaths = False
    headers = {}
    test_parse_next_pages = False

    emulate_javascript = False

    website_default_protocol = "http"

    JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY = "\n"
    JOIN_PARAGRAPHS_BY = "\n\n"

    do_not_complete_xpath_if_ends_with = ["@href", "text()", "@src", "text()[1]","text()[2]",
                                          "@alt"]

    multiple_items_per_page = False

    profiles_list = []

    @staticmethod
    def __initLogger___():
        # Only setup colored logs on dev environnement
        if env == "dev":
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.DEBUG)
            handler = colorlog.getLogger().handlers[0]
            handler.setFormatter(FRMT)
        pass
    def _init_xpaths(self):
        """ this functions is overrided to included any custom xpath to be used in a spider
        """
        pass

    def start_requests(self):
        if self.parse_profiles_from_index:
            for url in self.start_urls:
                yield Request(url=url,
                          callback=self.parse_profiles)

    def __initializeSpider__(self):
        """
        this methods allows for special initialization within spiders
        """

        self.source = self.name
        self.first_part = self.get_first_part()
        self.parse_data_page_method = self.parse_profile

    def __init__(self, force_refresh_profiles_data=False,
                    use_clearbit=None, clearbit_token=None, use_emailhunter=None,
                    emailhunter_token=None, test_mode=None, use_mongo="NO", *args, **kwargs):
        self.__initLogger___()
        self.__initializeSpider__()
        self._init_xpaths()

        for url in self.start_urls:
            if 'https' in url:
                logging.info("Website url (%s) uses https. OpenSSL version is: %s" % (url,
                ssl.OPENSSL_VERSION))

        self.force_refresh_profiles_data = (force_refresh_profiles_data == "YES")

        self.test_mode = False if test_mode == "NO" else self.test_mode

        if USE_CLEARBIT_API:
            self.use_clearbit = (use_clearbit == "YES")
            logging.info("use_clearbit in spider? %s" % str(self.use_clearbit))
        else:
            logging.info("Using clearbit api deactivated by default project settings.")

        self.clearbit_token = clearbit_token
        if not clearbit_token:
            self.clearbit_token = CLEARBIT_API_TOKEN
            logging.info("No clearbit token issued. Using default project token %s" % self.clearbit_token)
        else:
            logging.info("Using issued clearbit api token %s" % self.clearbit_token)

        if USE_EMAILHUNTER_API:
            self.use_emailhunter = (use_emailhunter == "YES")
            logging.info("use_emailhunter in spider? %s" % str(self.use_emailhunter))
        else:
            logging.info("Using emailhunter api deactivated by default project settings.")

        self.emailhunter_token = emailhunter_token
        if not emailhunter_token:
            self.emailhunter_token = EMAILHUNTER_API_TOKEN
            logging.info("No emailhunter token issued. Using default project token %s" %
                         self.emailhunter_token)
        else:
            logging.info("Using issued emailhunter api token %s" % self.clearbit_token)



        self.use_mongo = use_mongo
        if use_mongo != "YES":
            self.use_mongo = False
            logging.info("Not using mongo as requested by argument.")
            logging.info("Using clearbit api deactivated because not using mongodb.")
            logging.info("Using emailhunter api deactivated because not using mongodb.")
            self.use_emailhunter = False
            self.use_clearbit = False

        if self.is_test_mode():
            logging.info("Starting spider in test mode.")

        if self._do_emulate_javascript():
            logging.info("Emulating javascript pages.")

    def parse_profiles(self, response):
        if not self._get_xpath_from_xpaths('profiles'):
            logging.error("profiles xpath is undefined")
            return

        profiles = self.get_profiles_html_blocks(response)
        if self.is_test_mode():
            logging.info("Found %d profiles in url %s" % (len(profiles), response.url))
            profiles = profiles[:1]

        if self.multiple_items_per_page:
            for profile in profiles:
                if self._do_parse_profile({"body": profile}):
                    response = response.replace(body=profile)
                    il = ItemLoader(item=ProfileItem(), response=response)

                    il = self.populate_page_item_loader(response, il)
                    il = self.populate_profile_item_loader(response, il)

                    il = self.get_spider_specific_item_loader(response, il)
                    yield il.load_item()
        else:
            if self.is_test_mode() and self.test_profile_url:
                yield Request(url=self._make_complete_url(self.test_profile_url),
                              callback=self.parse_data_page_method)
            else:
                logging.debug("Found %d profiles in page %s." % (len(profiles), response.url))
                for profile_url in profiles:

                    # if self._profile_already_crawled(profile_url) or profile_url != "/our-people/richard-holway/":
                    if self._profile_already_crawled(profile_url):
                        logging.warning("Profile %s already crawled." % profile_url)
                    else:
                        self.profiles_list.append(profile_url)
                        if self._do_parse_profile({"profile_url": profile_url}):
                            yield Request(url=self._make_complete_url(profile_url),
                                      callback=self.parse_data_page_method)

        if self.is_test_mode() and self.test_parse_next_pages:
            pass
        else:
            yield self.get_next_page_request(response)

    def get_next_page_request(self, response):
        if self._get_xpath_from_xpaths('next_page_url'):
            next_page = response.xpath(self._get_xpath_from_xpaths('next_page_url')).extract_first()
            self._log_debug_xpath("Raw extracted next page : %s" % next_page)
            if next_page:
                self._log_debug_xpath("Full next page url: %s" % self._format_next_page(next_page, response))
                return Request(url=self._format_next_page(next_page, response),
                              headers=self.headers,
                              callback=self.parse_profiles)
        return None

    def _format_next_page(self, url, response=None):
        return self._make_complete_url(url)

    def parse_profile(self, response):
        """
        generic method for parsing pages
        :param response: Scrapy response object
        :return:
        """

        self.log("Parsing profile page (%s)" % response.url, logging.INFO)
        if self._do_ignore_profile_page(response):
            logging.info("Ignoring profile %s" % response.url)
            return None
        il = ItemLoader(item=ProfileItem(), response=response)
        il = self.populate_page_item_loader(response, il)
        il = self.populate_profile_item_loader(response, il)

        il = self.get_spider_specific_item_loader(response, il)
        return il.load_item()

    def populate_page_item_loader(self, response, il):
        """ populate item loader with generic page fields
        """
        il.add_value('url', response.url)
        il.add_xpath('canonical_url', self._get_xpath_from_xpaths('canonical_url'))
        il.add_xpath('page_title', self._get_xpath_from_xpaths('page_title'))

        il.add_value('source', self._get_source(response))
        il.add_value('spider', self.name)
        il.add_value('referer', response.request.headers.get('Referer'))
        il.add_value('scraped_date', datetime.now().strftime('%B %d, %Y'))
        il.add_value('scraped_date_native', datetime.now())

        il.add_value('company', self.company)
        il.add_value('company_url', self.company_url)

        return il

    def populate_profile_item_loader(self, response, itemLoader):
        """
        populates item loader from response
        :param response: response object from parse method
        :return: an item populated with data
        """

        # populate item from xpaths
        item_keys = ["company", "company_url", "profile_url", "profile_rss", "name_full",
                     "title",
                     "photo_url", "photo_file", "taxonomy_industry", "taxonomy_market",
                     "taxonomy_topics", "biography", "bio_blurb", "bio_speaker", "bio_education",
                     "bio_personal", "previous_bio", "previous_positions", "location", "languages",
                     "experience_company", "experience_industry", "experience", "certifications",
                     "memberships", "influence", "recognition", "ideas", "contact_briefing",
                     "contact_url", "contact_email", "contact_phone", "contact_mobile",
                     "contact_fax", "contact_other", "url_blog", "url_site", "twitter", "linkedin",
                     "slideshare", "facebook"]

        exclude_keys = ["profiles", "next_page_url"]

        itemLoader.add_value("profile_url", response.url)

        for key in self.xpaths:
            if key in exclude_keys:
                continue

            value = self.xpaths[key]

            if key not in item_keys:
                logging.warning("key %s not found in required fields." % key)
            else:
                raw_extracted_value = (self.format_extracted_value(response, key, value))
                raw_extracted_value = self._serialize_value(key, raw_extracted_value)
                itemLoader.add_value(key, raw_extracted_value)

        return itemLoader

    def _get_source(self, response):
        return self.source

    def get_spider_specific_item_loader(self, response, il):
        return il

    def format_extracted_value(self, response, key, value_dict):
        """
        :param value: value is the extracted result of xpath
        :return: formatted value to add as value in itemloader
        """
        xpath = value_dict["xpath"]
        value = []

        if not response.xpath(xpath) and value_dict.get("xpath_fallback"):
            xpath = value_dict["xpath_fallback"]

        for data_sel in response.xpath(xpath):

            sub_xpath = value_dict.get('sub_xpath', self._get_default_sub_xpath_for_key(xpath, key))

            if key in self.paragraph_item_keys:
                paragraph_html = data_sel.extract() # getting paragraph's html content (with tags)
                paragraph_html_cleaned_br = self._clean_paragraph_single_lines(paragraph_html, key)

                paragraph_selector = Selector(text=paragraph_html_cleaned_br)
                paragraphs = paragraph_selector.xpath('//descendant-or-self::text()').extract()
                paragraphs = self.format_paragraphs_list(paragraphs)

                one_value = ''.join(paragraphs)

            else:
                if sub_xpath:
                    one_value = ''.join([x.strip() for x in data_sel.xpath(sub_xpath).extract()
                                         if x is not None])

                else:
                    if isinstance(data_sel, list):
                        one_value = ''.join([x.strip() for x in data_sel.extract()
                                            if x is not None])

                    else:
                        one_value = data_sel.extract().strip()

            one_value = self.get_value_with_applied_regex(key, one_value)
            value.append(one_value)


        return value

    def get_value_with_applied_regex(self, key, value):
        regex = self.xpaths.get(key, {}).get('regex')
        force_regex = self.xpaths.get(key, {}).get('force_regex', False)
        # if force_regex is True
           # if there is no matched results then return empty data

        if regex:
            matched_regex = re.findall(regex, value)
            if matched_regex:
                return ''.join(matched_regex)
            else:
                if force_regex:
                    return ""

        return value

    def _make_complete_url(self, url):
        if self.website_default_protocol in url:
            return url
        return urlparse.urljoin(self.first_part, url)

    def get_first_part(self):
        if self.first_part:
            return self.first_part

        www_string = ""
        if self.add_www:
            www_string = "www."
        if not self.allowed_domains:
            return None
        first_part = self.website_default_protocol +'://' + www_string + self.allowed_domains[0]
        return first_part

    def _get_xpath_from_xpaths(self, key, default=None):
        xpath = self.xpaths.get(key, {}).get('xpath')
        if xpath:
           return xpath
        return default

    def _serialize_value(self, key, value):
        value = self.add_initial_serializer(key, value)

        if isinstance(value, list):
            value = [x.strip() for x in value if x]

        if key == "photo_url" and value:
            value = [self._make_complete_url(x) for x in value]

        if key == "taxonomy_market" and value:
            value = ','.join(value)

        if key == "taxonomy_industry" and value:
            value = ','.join(value)

        if key == "taxonomy_topics" and value:
            value = ','.join(value)

        if key == "experience" and value:
            value = ','.join(value)


        if key in self.paragraph_item_keys and value:
            if isinstance(value, list):
                value = [x.strip() for x in value if x.strip()]
                # value = '<<<<paragraph>>>>'.join(value)
                value = self.JOIN_PARAGRAPHS_BY.join(value)

            if isinstance(value, basestring):
                value = value.strip()

        if key == "twitter":
            value = ''.join(value)
            if "twitter.com" in value:
                matched_twitter_username = re.findall("twitter.com/(.+)", value)
                if matched_twitter_username:
                    value = matched_twitter_username[0]
                if 'twitter.com' in value:
                    return ''
            value = value.replace('/', '').replace('@', '')

        value = self.add_serializer(key, value)

        return value

    def add_serializer(self, key, value):
        return value

    def add_initial_serializer(self, key, value):
        return value

    def is_test_mode(self):
        if self.test_mode and env == "dev":
            return True
        return False

    def _get_default_sub_xpath_for_key(self, initial_xpath, key):
        for x in self.do_not_complete_xpath_if_ends_with:
            if initial_xpath.endswith(x):
                return None

        if key == "photo_url":
            return './@src'

        return './descendant-or-self::text()'

    def _log_debug_xpath(self, text):
        if self.is_test_mode() and self.debug_xpaths:
            logging.debug(text)

    def _clean_paragraph_single_lines(self, paragraph_html, key):
        paragraph_html_cleaned_br = (paragraph_html.replace("<br>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<br />", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<BR>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<BR />", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<br/>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY)
                                             .replace("<BR/>", self.JOIN_SINGLE_LINE_ON_PARAGRAPHS_BY))
        return paragraph_html_cleaned_br

    def get_profiles_html_blocks(self, response):
        return response.xpath(self._get_xpath_from_xpaths('profiles')).extract()

    def format_paragraphs_list(self, paragraphs):
        return paragraphs


    def _profile_already_crawled(self, profile_url):
        return profile_url in self.profiles_list

    def _do_ignore_profile_page(self, response):
        return False

    def _do_parse_profile(self, profile_url):
        return True

    def _do_emulate_javascript(self):
        return self.emulate_javascript

    def decode_cf_email(self, fp):
        r = int(fp[:2],16)
        email = ''.join([chr(int(fp[i:i+2], 16) ^ r) for i in range(2, len(fp), 2)])
        return email