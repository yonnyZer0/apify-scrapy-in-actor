#! /usr/bin/env python3

from scrapy import signals
import json
import os
import errno
import logging
from time import sleep

import datetime

from ..seq_store_conn import SeqStoreApify


__author__ = 'yonny'

class SequentialStoreReaderPipeline(object):

    def __init__(self, APIFY_TOKEN):
        self.conn = SeqStoreApify()
        self.conn.set_token(APIFY_TOKEN)
    
    @classmethod
    def from_crawler(cls, crawler):
    
        print('#################################')
        return cls( crawler.settings.get('APIFY_TOKEN') )#os.environ.get('APIFY_TOKEN')
        
    def open_spider(self, spider):
        self.store_id = json.loads( self.conn.create_store(spider.name)[0].decode() )['data']['id']
        #delete old store POC
        self.conn.delete_store(self.store_id)
        self.store_id = json.loads( self.conn.create_store(spider.name)[0].decode() )['data']['id']
    
    def close_spider(self, spider):
        #print(self.conn.get_records(self.store_id)[0])
        print('---------------------------------------------------------------------------------')
        print('JSON_LINK:','https://api.apify.com/v2/sequential-stores/' + self.store_id + '/records?format=json&limit=100000')
        print('STORE ID:',self.store_id)
        print('---------------------------------------------------------------------------------')
        #del self.conn
    
    def process_item(self, item, spider):
        
        item_x = item.__dict__['_values']
        
        item_x['scraped_date_native'][0]= item_x['scraped_date_native'][0].strftime('%s')     
        
        self.conn.put_record(self.store_id, str( json.dumps(item_x) ).encode() )
        
        return item


