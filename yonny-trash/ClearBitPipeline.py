__author__ = 'seni'

import logging
import requests
from scrapy import signals

CLEARBIT_TEST_RESPONSE = {
  "id": "d54c54ad-40be-4305-8a34-0ab44710b90d",
  "name": {
    "fullName": "Alex MacCaw",
    "givenName": "Alex",
    "familyName": "MacCaw"
  },
  "email": "alex@alexmaccaw.com",
  "gender": "male",
  "location": "San Francisco, CA, US",
  "timeZone": "America/Los_Angeles",
  "utcOffset": -8,
  "geo": {
    "city": "San Francisco",
    "state": "California",
    "stateCode": "CA",
    "country": "United States",
    "countryCode": "US",
    "lat": 37.7749295,
    "lng": -122.4194155
  },
  "bio": "O'Reilly author, software engineer & traveller. Founder of https://clearbit.com",
  "site": "http://alexmaccaw.com",
  "avatar": "https://d1ts43dypk8bqh.cloudfront.net/v1/avatars/d54c54ad-40be-4305-8a34-0ab44710b90d",
  "employment": {
    "domain": "clearbit.com",
    "name": "Clearbit",
    "title": "Founder and CEO",
    "role": "ceo",
    "seniority": "executive"
  },
  "facebook": {
    "handle": "amaccaw"
  },
  "github": {
    "handle": "maccman",
    "avatar": "https://avatars.githubusercontent.com/u/2142?v=2",
    "company": "Clearbit",
    "blog": "http://alexmaccaw.com",
    "followers": 2932,
    "following": 94
  },
  "twitter": {
    "handle": "maccaw",
    "id": "2006261",
    "bio": "O'Reilly author, software engineer & traveller. Founder of https://clearbit.com",
    "followers": 15248,
    "following": 1711,
    "location": "San Francisco",
    "site": "http://alexmaccaw.com",
    "avatar": "https://pbs.twimg.com/profile_images/1826201101/297606_10150904890650705_570400704_21211347_1883468370_n.jpeg"
  },
  "linkedin": {
    "handle": "pub/alex-maccaw/78/929/ab5"
  },
  "googleplus": {
    "handle": None
  },
  "angellist": {
    "handle": "maccaw",
    "bio": "O'Reilly author, engineer & traveller. Mostly harmless.",
    "blog": "http://blog.alexmaccaw.com",
    "site": "http://alexmaccaw.com",
    "followers": 532,
    "avatar": "https://d1qb2nb5cznatu.cloudfront.net/users/403357-medium_jpg?1405661263"
  },
  "aboutme": {
    "handle": "maccaw",
    "bio": "Software engineer & traveller. Walker, skier, reader, tennis player, breather, ginger beer drinker, scooterer & generally enjoying things :)",
    "avatar": "http://o.aolcdn.com/dims-global/dims/ABOUTME/5/803/408/80/http://d3mod6n032mdiz.cloudfront.net/thumb2/m/a/c/maccaw/maccaw-840x560.jpg"
  },
  "gravatar": {
    "handle": "maccman",
    "urls": [
      {
        "value": "http://alexmaccaw.com",
        "title": "Personal Website"
      }
    ],
    "avatar": "http://2.gravatar.com/avatar/994909da96d3afaf4daaf54973914b64",
    "avatars": [
      {
        "url": "http://2.gravatar.com/avatar/994909da96d3afaf4daaf54973914b64",
        "type": "thumbnail"
      }
    ]
  },
  "fuzzy": False
}

EMAILHUNTER_MIN_SCORE_ENABLED = False
MIN_EMAILHUNTER_SCORE = 90

class ClearBitPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(stats=crawler.stats)

        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        return pipeline

    def __init__(self, stats):
        self.stats = stats

    def spider_opened(self, spider):
        self.stats.set_value('clearbit_api_calls', 0)
        self.stats.set_value('clearbit_api_unknown_records', 0)
        self.stats.set_value('clearbit_api_calls_errors', 0)
        self.stats.set_value('clearbit_api_calls_success', 0)
        self.do_call_clearbit_api = spider.use_clearbit
        if self.do_call_clearbit_api:
            if not spider.clearbit_token:
                self.do_call_clearbit_api = False
            else:
                self.api_headers = {
                    "Authorization": "Bearer %s" % spider.clearbit_token
                }

    def process_item(self, item, spider):
        try:
            email = item.get('contact_email') or item.get('hunt_data_email') \
                    or item.get('clearbit_response', {}).get('email') # clearbit_response value
                    # can be set to None and thus result of item item.get('clearbit_response',
                    # {}) is None and ".get('email') fails. Try/catch is a hack around this.
        except:
            email = None

        if not email:
            # use emailhunter email
            emailhunter_score = item.get("eh_data_score", 0)
            emailhunter_email = item.get("hunt_data_email", 0)
            if EMAILHUNTER_MIN_SCORE_ENABLED:
                if emailhunter_score < MIN_EMAILHUNTER_SCORE:
                    logging.info("Ignoring item from clearbit pipeline. Reason: email not "
                                     "found. Detail : Email hunter email (%s) is not used because "
                                     "score (%d) < %d" %
                                    (emailhunter_email, emailhunter_score, MIN_EMAILHUNTER_SCORE))

        first_name = item.get('split_first_name')
        last_name = item.get('split_last_name')

        if not all([email]):
            logging.warning("Ignoring item from clearbit pipeline. Reason: Missing email.")
            return item

        if not self.do_call_clearbit_api:
            logging.debug("Reusing old clearbit data because not calling clearbit api")
            response_json = item.get('clearbit_response', {})
            if not response_json: response_json = {}
        elif item.get('dont_use_clearbit_pipeline'):
            logging.debug("Reusing old clearbit data because of 'dont_use_clearbit_pipeline' flag "
                          "in item")
            response_json = item['clearbit_response']
        elif spider.is_test_mode() and not item.get('dont_use_clearbit_pipeline'):
            logging.info("Using clearbit TEST_200_RESPONSE")
            response_json = CLEARBIT_TEST_RESPONSE
        else:
            api_url = ("https://person-stream.clearbit.com/v2/people/find?email=%s" % email)
            logging.debug("Calling clearbit api (url %s)." % api_url)
            self.stats.inc_value('clearbit_api_calls')
            response_json = requests.get(api_url,
                          headers=self.api_headers).json()
            if response_json.get('error'):
                if response_json.get('error', {}).get('type') == "unknown_record":
                    self.stats.inc_value('clearbit_api_unknown_records')
                    logging.info("Profile email %s not found using clearbit api.(Returned unknown record)"
                            % email)
                else:
                    self.stats.inc_value('clearbit_api_calls_errors')
                    logging.error("Error getting response data for email %s from page url %s. "
                                  "Response Error: "
                                  "%s" % (email, item.get('profile_url'), str(response_json.get('error'))))
                return item
            self.stats.inc_value('clearbit_api_calls_success')

        item["clearbit_response"] = response_json
        item = self.format_clearbit_itemfields(item, response_json)

        return item

    def format_clearbit_itemfields(self, item, clearbit_json_response):
        item["cb_indexed_at"] = clearbit_json_response.get("indexedAt")
        item["cb_name_full"] = clearbit_json_response.get("name", {}).get("fullName")
        item["cb_name_first"] = clearbit_json_response.get("name", {}).get("familyName")
        item["cb_name_last"] = clearbit_json_response.get("name", {}).get("givenName")
        item["cb_gender"] = clearbit_json_response.get("gender")
        item["cb_location"] = clearbit_json_response.get("location")
        item["cb_timezone"] = clearbit_json_response.get("timeZone")
        item["cb_utcoffset"] = clearbit_json_response.get("utcOffset")
        item["cb_geo_city"] = clearbit_json_response.get("geo", {}).get("city")
        item["cb_geo_state"] = clearbit_json_response.get("geo", {}).get("state")
        item["cb_geo_country"] = clearbit_json_response.get("geo", {}).get("country")
        item["cb_geo_lat"] = clearbit_json_response.get("geo", {}).get("lat")
        item["cb_geo_lon"] = clearbit_json_response.get("geo", {}).get("lng")
        item["cb_bio"] = clearbit_json_response.get("bio")
        item["cb_site"] = clearbit_json_response.get("site")
        item["cb_avatar"] = clearbit_json_response.get("avatar")
        item["cb_twitter_handle"] = clearbit_json_response.get("twitter", {}).get("handle")
        item["cb_twitter_id"] = clearbit_json_response.get("twitter", {}).get("id")
        item["cb_twitter_followers"] = clearbit_json_response.get("twitter", {}).get("followers")
        item["cb_twitter_location"] = clearbit_json_response.get("twitter", {}).get("location")
        item["cb_twitter_site"] = clearbit_json_response.get("twitter", {}).get("site")
        item["cb_twitter_statuses"]	= clearbit_json_response.get("twitter", {}).get("statuses")
        item["cb_twitter_avatar"] = clearbit_json_response.get("twitter", {}).get("avatar")
        item["cb_linkedin_handle"] = clearbit_json_response.get("linkedin", {}).get("handle")
        item["cb_facebook_handle"] = clearbit_json_response.get("facebook", {}).get("handle")
        item["cb_googleplus_handle"] = clearbit_json_response.get("googleplus", {}).get("handle")
        item["cb_aboutme_handle"] = clearbit_json_response.get("aboutme", {}).get("handle")
        item["cb_aboutme_bio"] = clearbit_json_response.get("aboutme", {}).get("bio")
        item["cb_aboutme_avatar"] = clearbit_json_response.get("aboutme", {}).get("avatar")
        item["cb_gravatar_handle"] = clearbit_json_response.get("gravatar", {}).get("handle")
        item["cb_gravatar_urls"] = clearbit_json_response.get("gravatar", {}).get("urls")
        item["cb_gravatar_avatar"] = clearbit_json_response.get("gravatar", {}).get("avatar")
        item["cb_gravatar_avatars"] = clearbit_json_response.get("gravatar", {}).get("avatars")
        item["cb_employment_name"] = clearbit_json_response.get("employment", {}).get("name")
        item["cb_employment_title"] = clearbit_json_response.get("employment", {}).get("title")
        item["cb_employment_role"] = clearbit_json_response.get("employment", {}).get("role")
        item["cb_employment_seniority"] = clearbit_json_response.get("employment", {}).get("seniority")
        item["cb_employment_domain"] = clearbit_json_response.get("employment", {}).get("domain")

        return item