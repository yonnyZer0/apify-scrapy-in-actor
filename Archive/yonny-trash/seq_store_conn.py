#! /usr/bin/env python

import urllib2 as u2
import os
import inspect

class Dataset(object):

    def set_token(self, APIFY_TOKEN):
    
        if APIFY_TOKEN == None:
            self.APIFY_TOKEN = os.environ['APIFY_TOKEN']
        else:
            self.APIFY_TOKEN = APIFY_TOKEN
        
    
    def __init__(self):
        
        self.default_seq_store_url = 'https://api.apify.com/v2/sequential-stores/'
    
    def get_filled_vars(self, args, values):
        
        filled = []
        for pair in [(i, values[i]) for i in args]:
            if pair[1] != None and pair[0] != 'storeId' and pair[0] != 'self':
                filled.append( pair[0] + '=' + str(pair[1]) )
        return filled

    def make_request(self, url, values=None, headers={}, method='GET'):
        
        url = url.strip('?')
        req = u2.Request( url, data=values, headers=headers)    
        
        try:
            
            if method == 'PUT':
                req.get_method = lambda: 'PUT'
                
            elif method == 'DELETE':
                req.get_method = lambda: 'DELETE'
            
            elif method == 'POST':
                req.get_method = lambda: 'POST'
            
            elif method == 'GET':
                req.get_method = lambda: 'GET'
            
            res = u2.urlopen(req)
            
            return res
            
        except Exception as ex:
        
            print(ex)
            return False    
    
    def get_list_of_stores(self, offset=None, limit=None, desc=None, unnamed=None):
        
        args, _, _, values = inspect.getargvalues( inspect.currentframe() )
               
        get_params = '?' + str.join('&', [ 'token=' + str(self.APIFY_TOKEN)] + self.get_filled_vars(args, values) )
        
        url = self.default_seq_store_url + get_params
        
        return self.make_request(url)
        
    def create_store(self, name):
        
        get_params = '?' + str.join('&',[ 'token=' + str(self.APIFY_TOKEN), 'name=' + str(name)])
        url = self.default_seq_store_url + get_params

        return self.make_request(url, method='POST')
    
    def get_store(self, storeId):
        
        url = self.default_seq_store_url + storeId
        
        return self.make_request(url, method='GET')
    
    def delete_store(self, storeId):
        
        url = self.default_seq_store_url  + storeId
        
        return self.make_request(url, method = 'DELETE')
    
    def get_records(self, storeId, format='json', offset=None, limit=None, fields=None, unwind=None, desc=None, attachment=None, delimiter=None, bom=None, xmlRoot=None, xmlRow=None):
    
        args, _, _, values = inspect.getargvalues( inspect.currentframe() )
               
        get_params = '?' + str.join('&', self.get_filled_vars(args, values) )
        
        url = self.default_seq_store_url + storeId + '/records' + get_params
        
        return self.make_request(url, method="GET")
    
    def put_record(self, storeId, payload):
  
        url = self.default_seq_store_url + storeId + '/records'
        
        return self.make_request(url, values=payload, headers={'Content-Type': 'application/json'}, method='POST')
        
    def save_to_kvstore(self, storeId, kvstoreId=None):
    
        if kvstoreId == None:
            kvstoreId = os.environ['APIFY_DEFAULT_KEY_VALUE_STORE_ID']
        url = 'https://api.apify.com/v2/key-value-stores/' + kvstoreId + '/records/out'
        
        return self.make_request(url, values={'seqstore': storeId}, headers={'Content-Type': 'application/json'}, method='PUT')
    
    
    
    
    
    
    
    
    
    
    
    
    
