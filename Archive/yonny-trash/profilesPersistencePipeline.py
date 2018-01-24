from scrapy import signals
import json
import os
import errno
import pymongo
import logging

__author__ = 'seni'



class ProfilesDBReaderPipeline(object):

    def __init__(self, stats, mongo_uri, mongo_collection, mongo_db):
        self.mongo_uri = mongo_uri
        self.collection_name = mongo_collection
        self.mongo_db = mongo_db
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(
            stats=crawler.stats,
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION'),
            mongo_db=crawler.settings.get('MONGO_DB')
            )
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        return pipeline

    def spider_opened(self, spider):
        if not spider.use_mongo:
            self.use_mongo = False
        else:
            self.use_mongo = True
            self.force_refresh_profiles_data = spider.force_refresh_profiles_data
            if self.force_refresh_profiles_data:
                logging.info("Force refresh profiles data. Ignoring all previous data ...")
            else:
                logging.info("Initializing mongo client %s. Pymongo version: %s ..." %
                              (self.mongo_uri, str(pymongo.version)))
                self.client = pymongo.MongoClient(self.mongo_uri)
                self.db = self.client[self.mongo_db]

                # try:
                spider.profiles_db = self.db[self.collection_name].find({"spider": spider.name})
                # profiles_list = []
                spider.profiles_db = list(spider.profiles_db)
                self.stats.set_value('profiles_read_from_db', len(spider.profiles_db))
                self.stats.set_value('matched_profiles_from_db', 0)

                # except:
                #     # The file is created, but empty so write new database to it.
                #     logging.critical("JSON file reading error from file %s." % filename)
                #     raise


    def read_JSONLines_file(self, file):
        data = []
        for line in file:
            data.append(json.loads(line))
        return data

    def _open_file(self, filename, option):
        # create folders if not exist
        if not os.path.exists(os.path.dirname(filename)):
            try:
                logging.debug("Making file %s" % filename)
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        if not os.path.exists(filename):
            logging.error("Creating file")
            return open(filename, "w+")
        return open(filename, option)

    def process_item(self, item, spider):
        if not self.use_mongo:
            return item

        if self.force_refresh_profiles_data:
            return item

        profile_exists = self.check_item_already_exists(item, spider)
        if profile_exists:
            self.stats.inc_value('matched_profiles_from_db')
            item['dont_use_emailhunter_pipeline'] = self.check_item_needs_emailhunter_pipeline(
                profile_exists)
            item['email_hunter_response'] = profile_exists.get('email_hunter_response')
            item['dont_use_clearbit_pipeline'] = self.check_item_needs_clearbit_pipeline(
                profile_exists)
            item['clearbit_response'] = profile_exists.get('clearbit_response')
            item['db_id'] = profile_exists.get('_id')
        return item

    def check_item_already_exists(self, item, spider):
        # check profile exists by profile url in profiles db
        profile_url = item['profile_url']
        profile_full_name = item.get('name_full')
        profile_first_name = item.get('split_first_name')
        profile_last_name = item.get('split_last_name')
        logging.debug("Checking if profile (%s) already exists from cursor ( %d results)"
                      % (profile_url, len(spider.profiles_db)))

        for profile in spider.profiles_db:
            if profile_full_name == profile.get('clearbit_response', {}).get('name',
                    {}).get('fullName'):
                logging.info("Found profile %s by matching scraped full name %s with "
                              "clearbit_response fullName %s" %(profile_url, profile_full_name,
                profile.get('clearbit_response', {}).get('name',
                    {}).get('fullName')))
                return profile

            if ((profile_first_name == profile.get('clearbit_response', {}).get('name',
                    {}).get('givenName')
                  and profile_last_name == profile.get('clearbit_response', {}).get('name',
                        {}).get('familyName'))
            or (profile_last_name == profile.get('clearbit_response', {}).get('name',
                        {}).get('givenName')
                  and profile_first_name == profile.get('clearbit_response', {}).get('name',
                            {}).get('familyName'))):
                logging.debug("Profile already exists by first and last name(url = %s)" % str(
                    profile_url))
                return profile

            logging.debug("Checking profileurl %s against db profileurl: %s" % (profile_url,
                                                                                profile['profile_url']))
            if profile_url == profile['profile_url']:
                if spider.multiple_items_per_page:
                    return
                logging.debug("Profile already exists (url = %s)" % str(profile_url))
                return profile


        logging.debug("NO Profile does not already exist (url = %s)" % str(profile_url))

        return

    # check if profile needs to be passed to emailhunter pipeline
    def check_item_needs_emailhunter_pipeline(self, profile):
        item_has_email = any([
                bool(profile.get('contact_email')),
                bool(profile.get('hunt_data_email')),
                profile.get('email_hunter_response')
            ])
        logging.debug("Profile %s already has email? %s" % (profile.get('profile_url'), str(item_has_email)))
        return item_has_email

    # check if profile needs to be passed to clearbit pipeline
    def check_item_needs_clearbit_pipeline(self, profile):
        return bool(profile.get('clearbit_response'))

class ProfilesPersistencePipeline(object):

    def __init__(self, stats, mongo_uri, mongo_collection, mongo_db):
        self.mongo_uri = mongo_uri
        self.collection_name = mongo_collection
        self.mongo_db = mongo_db
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(
            stats=crawler.stats,
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_collection=crawler.settings.get('MONGO_COLLECTION'),
            mongo_db=crawler.settings.get('MONGO_DB'))
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        return pipeline

    def spider_opened(self, spider):
        if spider.use_mongo:
            logging.debug("Initializing mongo client...")
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]

            self.stats.inc_value('inserted_profiles_in_db', 0)
            self.stats.inc_value('updated_profiles_in_db', 0)

    def process_item(self, item, spider):
        if not spider.use_mongo:
            return item

        if not item.get('clearbit_response') or 'error' in item.get('clearbit_response', {}):
            logging.debug("CLEARBIT_RESPONSE field is empty or contains error. Not updating "
                             "this field in db. (Clearbit_response = %s)" % str(item.get(
                'clearbit_response')))
            if 'clearbit_response' in item:
                item.pop('clearbit_response')
        else:
            logging.debug("Clearbit_response field is populated with data. Updating this field.")

        if 'db_id' in item:
            self.stats.inc_value('updated_profiles_in_db')
            self.db[self.collection_name].update({'_id': item['db_id']},
                                                {'$set': self.serialize_item(item)},
                                                upsert=True)
        else:
            self.stats.inc_value('inserted_profiles_in_db')
            self.db[self.collection_name].update({'profile_url': item['profile_url']},
                                                    {'$set': self.serialize_item(item)},
                                                    upsert=True)
        return item

    def serialize_item(self, item):
        for k,v in item.iteritems():
            item[k] = "" if not v else v
        return dict(item)
