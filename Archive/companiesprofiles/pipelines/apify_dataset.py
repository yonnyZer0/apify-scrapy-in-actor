#! /usr/bin/env python3

from scrapy import signals
import json
import os
import errno
import logging
from time import sleep

import datetime

from ..py2_apify import ApifyClient


__author__ = 'yonny'

class DatasetPush(object):

    def __init__(self):
        self.client = ApifyClient()
    
    @classmethod
    def from_crawler(cls, crawler):
  
        return cls()
    
    def process_item(self, item, spider):
        
        item_x = item.__dict__['_values']
        
        item_x['scraped_date_native'][0]= item_x['scraped_date_native'][0].strftime('%s')     
        
        self.client.pushRecords( options={ 'data': item_x} )
        print('################################################################')
        return item


