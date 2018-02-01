#! /usr/bin/env python

import urllib2 as u2
import os

class ApifyClient(object):
    
    options = {'contentType': 'application/json', 'expBackOffMaxRepeats': 8, 'expBackOffMillis': 500, 'data': {} }
    
    ## simple function for pushing records
    
    def pushRecords(self, options):
        
        _options = self.merge_options(options)
         
        url = 'https://api.apify.com/v2/datasets/' + _options['APIFY_DEFAULT_DATASET_ID'] + '/records'
        
        return self.make_request(url, values=_options['data'], headers={'Content-Type': _options['contentType']}, method='POST')
    
    ## Add timeout/delay to repeat
    def make_request(self, url, values=None, headers={}, method='GET'):
            
        url = url.strip('?')
        
        if type( values ) is dict:
            values = str( json.dumps( values ) ).encode()
        
        req = u2.Request( url, data=values, headers=headers)    
        
        #self.last_exec_response = False
        for i in range( options['expBackOffMaxRepeats'] ):
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
                
                #self.last_exec_response = res
                            
                return res.read()
                
            except Exception as ex:
            
                print(ex)
                return False
            sleep( self.options['expBackOffMillis'] / 1000 )
                
        return False
    ## Merges options
    def merge_options(self, options):
    
        _options = dict( self.options )
        _options.update(options)
        
        return _options 

    def __init__(self, options={}):
    
        for env in ['APIFY_ACT_ID', 'APIFY_ACT_RUN_ID', 'APIFY_USER_ID', 'APIFY_TOKEN', 'APIFY_STARTED_AT', 'APIFY_TIMEOUT_AT', 'APIFY_DEFAULT_KEY_VALUE_STORE_ID', 'APIFY_DEFAULT_DATASET_ID', 'APIFY_WATCH_FILE', 'APIFY_HEADLESS', 'APIFY_MEMORY_MBYTES']:
            if env in os.environ:
                self.options[ env ] = os.environ.get(env)
        
        self.options = options
        
        self.keyValueStores = self.KeyValueStores(self.options, self.make_request, self.merge_options)
        self.datasets = self.Datasets(self.options, self.make_request, self.merge_options)
    
    def setOptions(self, options):
        
        self.options.update(options)
        
        self.keyValueStores.options = self.options
        self.datasets.options = self.options
    
    def getOptions(self):
    
        return self.options
    
    ## KVSTORES
    class KeyValueStores(object): 
        
        def __init__(self, options, make_request, merge_options):
            
            self.options = options
            self.make_request = make_request
            self.merge_options = merge_options
            
            self.defaultKeyValueStoresUrl = 'https://api.apify.com/v2/key-value-stores/'     
               
    ## DATASETS
    class Datasets(object):
             
        def __init__(self, options, make_request, merge_options):
            
            self.options = options
            self.make_request = make_request
            self.merge_options = merge_options
            
            self.defaultDatasetsUrl = 'https://api.apify.com/v2/datasets/'
            self.last_exec_response = False
        
        def deleteStore(self, options={}):
            
            _options = self.merge_options(options)
            
            url = self.defaultDatasetsUrl  + _options['datasetId']
            
            return self.make_request(url, headers={'Content-Type': _options['contentType']}, method = 'DELETE')
            
        def getDataset(self, options={}):
            
            _options = self.merge_options(options)
                        
            url = self.defaultDatasetsUrl + _options['datasetId']
            
            return self.make_request(url, headers={'Content-Type': _options['contentType']}, method='GET')
        
        def getItems(self, options={}):
            
            _options = self.merge_options(options)
            
            url = self.defaultDatasetsUrl + _options['datasetId'] + '/records' + get_params
            
            return self.make_request(url, headers={'Content-Type': _options['contentType']}, method="GET")
        
        def getOrCreateDataset(self, options={}):
            
            _options = self.merge_options(options) 
            
            url = self.defaultDatasetsUrl + get_params

            return self.make_request(url, headers={'Content-Type': _options['contentType']}, method='POST')
            
        def listDatasets(self, options={}):
            
            _options = self.merge_options(options)
            #get_params = '?' + str.join('&', [ 'token=' + str(self.token)] + self.get_filled_vars(args, values) )
            url = self.defaultDatasetsUrl + get_params
            
            return self.make_request(url)
        
        def putItems(self, options={}):
            
            _options = self.merge_options(options)
            
            url = self.defaultDatasetsUrl + _options['datasetId'] + '/records'
            
            return self.make_request(url, values=options['data'], headers={'Content-Type': _options['contentType']}, method='POST')
    
    
    
    
    
    

