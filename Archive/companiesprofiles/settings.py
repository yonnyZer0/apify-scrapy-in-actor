
import os

BOT_NAME = 'companiesprofiles'

SPIDER_MODULES = ['companiesprofiles.spiders']
NEWSPIDER_MODULE = 'companiesprofiles.spiders'

env = os.getenv("SCRAPY_ENV", "prod")
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'

ITEM_PIPELINES = {
    
    'companiesprofiles.pipelines.TextProcessingPipeline.TextProcessingPipeline': 300,
    'companiesprofiles.pipelines.seq_store_integration.SequentialStoreReaderPipeline': 350,
    
    #'companiesprofiles.pipelines.profilesPersistencePipeline.ProfilesDBReaderPipeline': 350,
    #'companiesprofiles.pipelines.EmailFinderPipeline.EmailFinderPipeline': 400,
    #'companiesprofiles.pipelines.ClearBitPipeline.ClearBitPipeline': 500,
    #'companiesprofiles.pipelines.profilesPersistencePipeline.ProfilesPersistencePipeline': 900,
    #'companiesprofiles.pipelines.ItemScrapingHubCSVPipeline.ItemScrapingHubCSVPipeline': 1000,

}

HTTPCACHE_ENABLED = False

FEED_EXPORT_FIELDS = ["scraped_date", "company", "company_url", "profile_url", "profile_rss",
                      "name_full",
                      "photo_url", "photo_file", "title", "taxonomy_industry", "taxonomy_market",
                      "taxonomy_topics", "biography", "bio_blurb", "bio_speaker", "bio_education",
                      "bio_personal", "previous_bio", "previous_positions", "location", "languages",
                      "experience_company", "experience_industry", "experience", "certifications",
                      "memberships", "influence", "recognition", "ideas", "contact_briefing",
                      "contact_url", "contact_email", "contact_phone", "contact_mobile",
                      "contact_fax", "contact_other", "url_blog", "url_site", "twitter", "linkedin",
                      "slideshare", "facebook", "hunt_data_email", "eh_data_score", "eh_data_domain",
                      "eh_meta_params_name_first", "eh_meta_params_name_last",
                      "eh_meta_params_domain", "eh_meta_params_company", "cb_indexed_at",
                      "cb_name_full", "cb_name_first", "cb_name_last", "cb_gender", "cb_location",
                      "cb_timezone", "cb_utcoffset", "cb_geo_city", "cb_geo_state", "cb_geo_country",
                      "cb_geo_lat", "cb_geo_lon", "cb_bio", "cb_site", "cb_avatar",
                      "cb_twitter_handle", "cb_twitter_id", "cb_twitter_followers",
                      "cb_twitter_location", "cb_twitter_site", "cb_twitter_statuses",
                      "cb_twitter_avatar", "cb_linkedin_handle", "cb_facebook_handle",
                      "cb_googleplus_handle", "cb_aboutme_handle", "cb_aboutme_bio",
                      "cb_aboutme_avatar", "cb_gravatar_handle", "cb_gravatar_urls",
                      "cb_gravatar_avatar", "cb_gravatar_avatars", "cb_employment_name",
                      "cb_employment_title", "cb_employment_role", "cb_employment_seniority",
                      "cb_employment_domain"]

# AMAZON S3 SETTINGS
"""AWS_ACCESS_KEY_ID = "AKIAIJJJLU37F7EJ4PJQ"
AWS_SECRET_ACCESS_KEY = "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"

MONGO_URI = "mongodb://imad:robert16@ds133438.mlab.com:33438/profilesdb"
MONGO_DB = "profilesdb"
MONGO_COLLECTION = "profiles"

"""

APIFY_TOKEN=None

# CLEARBIT API
USE_CLEARBIT_API = False #yonny comment out
CLEARBIT_API_TOKEN = "sk_29c4a6973d61ebeb2aee4552da8a7c3f"

# EMAILHUNTER API
USE_EMAILHUNTER_API = False #yonny comment out
EMAILHUNTER_API_TOKEN = "a6d383732f7011f32f4d4c0a6fc5dfa776b47c2e"

LOG_LEVEL = 'DEBUG'
