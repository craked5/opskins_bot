import json
import time
import requests
import cfscrape
import datetime
import unicodedata
import redis
import sys

try:
    config_details = json.load(open('utils/config.json','r'))
except:
    print "cant open the config file, check it please!"
    print "exiting now!"
    sys.exit()

r = redis.StrictRedis(host=config_details["redis_server"], port=6379)
condition_list = [' (Factory New)', ' (Minimal Wear)', ' (Field-Tested)', ' (Well-Worn)', ' (Battle-Scarred)']
opskins_api_key = unicodedata.normalize('NFKD', config_details["opskins_api_key"]).encode('ascii','ignore')
scraper = cfscrape.create_scraper()
date_now = datetime.datetime.now().strftime("%b %d, %Y").lstrip("0").replace(" 0", " ")

def get_price_history(item):

    time.sleep(1.5)
    res = requests.get('https://opskins.com/api/price_api.php?request=GetPriceHistory&key='
                    + opskins_api_key + '&name=' + item)
    print res.url
    print res.content
    item_info_temp = json.loads(res.content)

    if 'result' in item_info_temp:
        print "Could not get item: " + item
        print "Maybe it does not exists or theres no data for the item."
        return False
    else:
        return item_info_temp

item_temp = raw_input('What item(s) do you want to check? ("all" for all items on file) ')
json_history_file = open('utils/items_history_opskins.json', 'r')
item_history_json = json.load(json_history_file)
json_history_file.close()

if item_temp != 'all':
    item_history = get_price_history(item_temp)
    print r.set(item_temp, item_history)
    item_history_json[item_temp] = item_history
    with open('utils/items_history_opskins.json', 'w') as temp_file:
        json.dump(item_history_json, temp_file)
        temp_file.close()
else:
    with open('utils/csgoitems.txt', 'r') as item_file:
        file_items_name = [line.rstrip() for line in item_file]
        for item in file_items_name:
            if "Case Key" in item:
                item_history = get_price_history(item)
                if item_history != False:
                    print r.set(item, item_history)
                    item_history_json[item] = item_history
                    item_history_json[item]["manual_price"] = 0
                else:
                    print 'failed getting price history for ' + item
            else:
                for condition in condition_list:
                    item_history = get_price_history(item+condition)
                    if item_history != False:
                        print r.set(item+condition, item_history)
                        item_history_json[item+condition] = item_history
                        item_history_json[item+condition]["manual_price"] = 0
                    else:
                        print 'failed getting price history for ' + item+condition
        with open('utils/items_history_opskins.json', 'w') as temp_file:
            json.dump(item_history_json, temp_file)
            temp_file.close()