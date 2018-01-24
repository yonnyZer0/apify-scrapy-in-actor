
import logging
from scrapy import signals
import requests

__author__ = 'seni'

TEST_200_RESPONSE =  {
    "data" : {
      "email": "dnorfolk@bloor.eu",
      "score": 72,
      "sources": [
        {
          "domain" : "blog.asana.com",
          "uri" : "http://blog.asana.com",
          "extracted_on" : "2015-09-27"
        }
      ],
    },
    "meta" : {
      "params" : {
        "first_name" : "Dustin",
        "last_name" : "Moskovitz",
        "domain" : "stripe.com",
        "company" : None

      }
    }
  }

class EmailFinderPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(stats=crawler.stats)

        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        return pipeline

    def __init__(self, stats):
        self.stats = stats

    def spider_opened(self, spider):
        self.stats.set_value('emailhunter_api_calls', 0)
        self.do_call_emailhunter_api = spider.use_emailhunter
        if self.do_call_emailhunter_api:
            if not spider.emailhunter_token:
                self.do_call_emailhunter_api = False
            else:
                self.emailhunter_token = spider.emailhunter_token

    def process_item(self, item, spider):
        # domain_name = item.get("company_url")
        try:
            domain_name = spider.allowed_domains[0]
        except:
            logging.error("Error extracting domain name to make emailhunter request. Dropping item")
            return
        first_name = item.get('split_first_name')
        last_name = item.get('split_last_name')

        if item.get('contact_email'):
            logging.info("Email already existing for item %s. Ignoring item from email finder "
                         "pipeline" % item.get('profile_url'))
            return item

        if not all([domain_name, first_name, last_name]):
            logging.warning("Missing domain, first name or last name. Ignoring item %s from email "
                            "finder pipeline." % item.get('profile_url'))
            return item

        if not self.do_call_emailhunter_api:
            logging.debug("Reusing old emailhunter data because not calling emailhunter api")
            response_json = item.get('emailhunter_response', {})
            if not response_json: response_json = {}

        # elif spider.test_mode and not item.get('dont_use_emailhunter_pipeline'):
        #     logging.info("Using email hunter TEST_200_RESPONSE")
        #     response_json = TEST_200_RESPONSE
        elif item.get('dont_use_emailhunter_pipeline'):
            logging.debug("Reusing old emailhunter data")
            response_json = item['email_hunter_response']
        else:
            api_url = ("https://api.hunter.io/v2/email-finder?domain=%s&first_name=%s"
                      "&last_name=%s&api_key=%s" % (domain_name, first_name, last_name, self.emailhunter_token))

            logging.debug("Calling email hunter api (url %s)." % api_url)
            self.stats.inc_value('emailhunter_api_calls')
            response_json = requests.get(api_url).json()
            logging.debug("Received response %s from email hunter (api url called: %s" % (str(
                response_json), api_url))
        item["email_hunter_response"] = response_json

        item = self.format_emailhunter_data(item, response_json)

        return item

    def format_emailhunter_data(self, item, emailhunter_json_response):

        item["hunt_data_email"] = emailhunter_json_response.get("data", {}).get("email")
        item["eh_data_score"] = emailhunter_json_response.get("data", {}).get("score")
        item["eh_data_domain"] = emailhunter_json_response.get("data", {}).get("domain")
        item["eh_meta_params_name_first"] = emailhunter_json_response.get("meta", {}).get("params", {}).get("first_name")
        item["eh_meta_params_name_last"] = emailhunter_json_response.get("meta", {}).get("params", {}).get("last_name")
        item["eh_meta_params_domain"] = emailhunter_json_response.get("meta", {}).get("params", {}).get("domain")
        item["eh_meta_params_company"] = emailhunter_json_response.get("meta", {}).get("params", {}).get("company")

        return item


