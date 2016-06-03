import redis
import ujson
import sys
import onetimepass
import requests

try:
    config_details = ujson.load(open('utils/config.json', 'r'))
except:
    print "cant open the config file, check it please!"
    print "exiting now!"
    sys.exit()

api= config_details["bitskins_api_key"]
# get a token that's valid right now
my_secret = config_details["bitskins_secret"]

r = redis.StrictRedis(host=config_details["redis_server"], port=6379)

condition_list = [' (Factory New)', ' (Minimal Wear)', ' (Field-Tested)', ' (Well-Worn)', ' (Battle-Scarred)']

def get_price_history(item, my_token):

    res = requests.get("https://bitskins.com/api/v1/get_price_data_for_items_on_sale/?api_key="+api
                         +"&code="+str(my_token)+"&names="+item)
    print res.url
    item_info_temp = ujson.loads(res.content)

    if item_info_temp["data"]["items"][0]["total_items"] == 0:
        print "Could not get item: " + item
        print "Maybe it does not exists or theres no data for the item."
        return False
    else:
        print "Lowest price for item "+ item + " --> " + str(item_info_temp["data"]["items"][0]["lowest_price"])
        return item_info_temp

item_temp = raw_input('What item(s) do you want to check? ("all" for all items on file) ')
if item_temp != 'all':
    my_token = onetimepass.get_totp(my_secret)
    item_history = get_price_history(item_temp, my_token)
    print r.set(item_temp+"_bitskins", item_history)

else:
    with open('utils/csgoitems.txt', 'r') as item_file:
        file_items_name = [line.rstrip() for line in item_file]
        for item in file_items_name:
            my_token = onetimepass.get_totp(my_secret)
            if "Case Key" in item:
                item_history = get_price_history(item, my_token)
                if item_history != False:
                    print r.set(item+"_bitskins", item_history)
                else:
                    print 'failed getting price history for ' + item
            else:
                for condition in condition_list:
                    item_history = get_price_history(item+condition, my_token)
                    if item_history != False:
                        print r.set(item+condition+"_bitskins", item_history)
                    else:
                        print 'failed getting price history for ' + item+condition