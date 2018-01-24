#! /usr/bin/env python3

import urllib2 as u2
import os
#import urllib.parse
import inspect

class SeqStoreApify(object):

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
        print( url )
        
        try:
            
            if method == 'PUT':
                req = u2.Request( url )
                req.get_method = lambda: 'PUT'
                req.data=values
                req.add_header('Content-Type', 'application/json')
                
            elif method == 'DELETE':
                req = u2.Request( url, data=values, headers=headers)
                req.get_method = lambda: 'DELETE'
            
            elif method == 'POST':
                req = u2.Request( url, data=values, headers=headers)
                req.get_method = lambda: 'POST'
            
            elif method == 'GET':
                req = u2.Request( url, data=values, headers=headers)
                req.get_method = lambda: 'GET'
            
            """elif method == 'GET 2':
                req = requests.get(url)
                return req.content"""
            
            res = u2.urlopen(req)
            
            return [res.read(), res]
            
        except Exception as ex:
        
            print(ex)
            return        
    
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
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        return self.make_request(url, values=payload, headers={'Content-Type': 'application/json'}, method='POST')
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
