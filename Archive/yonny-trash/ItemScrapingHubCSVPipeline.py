__author__ = 'seni'

ITEM_EXPORT_KEYS = ["scraped_date", "company", "company_url", "profile_url", "profile_rss",
                      "name_full",
                      "photo_url", "photo_file", "title", "taxonomy_industry", "taxonomy_market",
                      "taxonomy_topics", "biography", "bio_blurb", "bio_speaker", "bio_education",
                      "bio_personal", "previous_bio", "previous_positions", "location", "languages",
                      "experience_company", "experience_industry", "experience", "certifications",
                      "memberships", "influence", "recognition", "ideas", "contact_briefing",
                      "contact_url", "contact_email", "contact_phone", "contact_mobile",
                      "contact_fax", "contact_other", "url_blog", "url_site", "twitter", "linkedin",
                      "slideshare", "facebook",
                      "username", "simplified_joined_name", "split_title", "split_first_name",
                      "split_mid_name", "split_last_name", "split_suffix",
                      "hunt_data_email", "eh_data_score", "eh_data_domain",
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

class ItemScrapingHubCSVPipeline(object):
    def process_item(self, item, spider):
        for key in ITEM_EXPORT_KEYS:
            if key not in item:
                item[key] = ''

        return item