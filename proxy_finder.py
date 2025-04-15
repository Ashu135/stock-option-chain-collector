import requests
from lxml.html import fromstring
from pymongo import MongoClient
from datetime import datetime

def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url,verify = False)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')][0])
            proxies.add(proxy)
    return proxies

def save_to_mongodb(proxies):
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['proxy_db']
        collection = db['proxies']
        
        # Create document to insert
        proxy_doc = {
            'timestamp': datetime.now(),
            'proxies': list(proxies)
        }
        
        # Insert the document
        collection.insert_one(proxy_doc)
        print(f"Successfully saved {len(proxies)} proxies to MongoDB")
        
    except Exception as e:
        print(f"Error saving to MongoDB: {str(e)}")
    finally:
        client.close()
