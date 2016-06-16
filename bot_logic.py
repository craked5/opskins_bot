#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import smtplib
import requests
import re
import logbook
import time
import cfscrape
import redis
import glws_conn
import datetime
import timeit
import unicodedata
import sys
from bs4 import BeautifulSoup
from collections import OrderedDict

class mainLogic:

    def __init__(self):

        try:
            config_details = json.load(open('utils/config.json','r'))
        except:
            print "cant open the config file, check it please!"
            print "exiting now!"
            sys.exit()
        self.redis_client = redis.StrictRedis(host=config_details["redis_server"], port=6379)
        self.logger = logbook.Logger(time.strftime("%d/%m/%Y %H:%M:%S") + ' Opskins logger')
        log = logbook.FileHandler('utils/loggingfile.txt')
        log.push_application()
        self.email_number = 0
        self.last_opsid_from_site = []
        self.scraper = cfscrape.create_scraper()
        self.opskins_recent_url = "https://opskins.com/ajax/browse_scroll.php?page=1&appId=730&contextId=2"
        self.opskins_balance = 0
        self.item_price_history_sorted = {}
        self.trys_counter = 0
        self.opskins_api_key = unicodedata.normalize('NFKD', config_details["opskins_api_key"]).encode('ascii','ignore')
        self.email_username = config_details['email_username']
        self.email_password = config_details['email_password']
        self.FROM = config_details['email_username']
        self.TO = config_details['email_to_send']
        self.discount_percentage = float(config_details['discount_percentage'])
        self.min_item_price = float(config_details['min_item_price'])
        self.send_email_bool = bool(config_details['send_email'])
        self.server_ip = str(config_details['server_ip'])
        self.using_redis = bool(config_details['using_redis'])
        self.opskins_headers = {
            "accept": "application/json",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Language": "pt-PT,pt;,q = 0.8,en-US;q=0.6,en;q=0.4,fr;q=0.2,es;q=0.2",
            "Cache-Control": "no-cache",
            "DNT": "1",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla / 5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
        }

        if self.using_redis:
            print "USING REDIS AS STORAGE!"
            try:
                item_price_history = {}
                for key in self.redis_client.scan_iter():
                    key_good = key.decode("utf-8")
                    item_price_history[key_good] = self.redis_client.get(key.decode("utf-8"))
                print len(item_price_history)
                if self.sort_prices(item_price_history):
                    print "sorted item price dict good"
                print "Opened items price history with success!"
            except:
                print "Problem opening the redis db!!"
        else:
            print "USING FILE AS STORAGE!"
            try:
                temp_file = open('utils/items_history_opskins.json', 'r')
                item_price_history = json.load(temp_file)
                temp_file.close()
                if self.sort_prices(item_price_history):
                    print "sorted item price dict good"
                print "Opened items price history with success!"
            except:
                print "Problem opening the items price history file, maybe it does not exist, try doing doing the command gethistory"

    def start_smtp(self, email_username, email_password):

        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.ehlo()
        self.server.starttls()
        try:
            self.server.login(email_username, email_password)
            print 'LOGIN IS DONE YEYYY, YOU CAN NOW SEND SHIT EMAILS. xD'
            return True
        except smtplib.SMTPHeloError:
            print 'The server responded weird stuff to my login request, please try again'
            return False
        except smtplib.SMTPAuthenticationError:
            print 'Your account name or password is incorrect, please try again using the correct stuff'
            return False
        except smtplib.SMTPException:
            print 'SHIT IS ALL FUCKED THERES NO HOPE THE WORLD IS GOING TO END, HIDEE '
            return False

    def send_email_new_item(self, FROM, TO, TEXT, item_name):

        SUBJECT = 'New potencial item: %s' % item_name
        try:
            message = """\From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
            self.server.sendmail(FROM, TO, message)
            self.email_number += 1
            print 'Email number '+ str(self.email_number) + ' was sent for the item ' + item_name

        except smtplib.SMTPRecipientsRefused:
            print 'The email was not sent, the target refused'
            return False
        except smtplib.SMTPServerDisconnected:
            print 'The server is disconnected.'
            return False
        except:
            print 'SHIT HAPPENED DEAL WITH IT'
            return False

    def get_opskins_html(self, page, *args):

        op_codes = ['pricelh', 'pricehl', 'floatlh', 'floathl']

        list_params = ['search_item', 'min', 'max', 'grade', 'type', 'sort', 'StatTrak', 'vanilla']

        bad_querie_list = args[0].split('&')

        opdata = OrderedDict([('search_item',''), ('StatTrak',''), ('grade',''), ('type',''),
                              ('sort',''), ('min',''), ('max',''), ('vanilla',False)])

        for subl in bad_querie_list:
            for param in list_params:
                if param in subl:
                    if param == 'search_item':
                        opdata[param] = subl.split("=",1)[1].replace('+', ' ')
                    else:
                        opdata[param] = subl.split("=",1)[1]

        params_tuple = (('type', 'scroll'), ('page', str(page)), ('data', json.dumps(opdata, separators=(',', ':'))))

        url_querie = 'https://opskins.com/ajax/search_scroll.php?'
        opskins_resp = self.scraper.get(url_querie, params=params_tuple)

        print opskins_resp.url

        return opskins_resp
    
    def get_opskins_weapon_prices(self, pages, link):
        
        print pages
        page = 1
        
        while page <= int(pages):
            print page

            data = self.get_opskins_html(page, link)

            if data.status_code == 200:
                soup = BeautifulSoup(data.content,'lxml')

                items_bad = soup.find_all('div', {'class':'featured-item col-xs-12 col-sm-6 col-md-4 col-lg-3 center-block'})
                
                for item in items_bad:
                    item_url = str(item.find('a',{'class':'btn btn-primary'})['href'])

                    print "Page: " + str(page)
                    print "Item name: " + item.find('a',{'class':'market-name market-link'}).text.encode('utf-8')
                    print "Item price: " + str(item.find('div',{'class':'item-amount'}).text)
                    print "Item float: " + item.find('i', {'class':'glyphicon glyphicon-triangle-bottom'
                                                           })['title'].split(':')[1].strip()
                    #suggested price
                    print item.find('span',{'class':'market-name'}).text
                    print "Item opskins url: " + str(item.find('a',{'class':'market-name market-link'})['href']) + "\n\n"

            page += 1

    def get_opskins_weapon_info(self, pages, link):

        self.st = glws_conn.makeSocket()
        print "Socket ready: " + str(self.st.emitready())

        print pages
        page = 1
        
        while page <= int(pages):
            print page

            data = self.get_opskins_html(page, link)

            if data.status_code == 200:
                soup = BeautifulSoup(data.content,'lxml')

                items_bad = soup.find_all('div', {'class':'featured-item col-xs-12 col-sm-6 col-md-4 col-lg-3 center-block'})

                for item in items_bad:
                    isdict = False

                    item_url = str(item.find('a',{'class':'btn btn-primary'})['href'])

                    while isdict is False:
                        float_dict = self.st.emitgetdata({"link":item_url})

                        if type(float_dict) is dict:
                            isdict = True
                            print "Page: " + str(page)
                            print "Item name: " + item.find('a',{'class':'market-name market-link'}).text.encode('utf-8')
                            print "Paint Index: " + str(float_dict['skin']['paintindex'])
                            print "Item float: " + item.find('i', {'class':'glyphicon glyphicon-triangle-bottom'
                                                                   })['title'].split(':')[1].strip()
                            print "Item id: " + str(float_dict['skin']['itemid'])
                            print "Item price: " + str(item.find('div',{'class':'item-amount'}).text)
                            #suggested price
                            print item.find('span',{'class':'market-name'}).text
                            print "Item opskins url: " + str(item.find('a',{'class':'market-name market-link'})['href']) + "\n\n"

            page += 1

    #If this returns 0 its because the current items on the website are equal to the item_list
    #If this returns 1 its because the current items on the website are updated and we must check for new prices
    def check_recent_opskins(self):

        #items that pass the price formula
        return_list = []
        items_to_email = {}

        start_time = timeit.default_timer()

        try:
            opsres = requests.get(self.opskins_recent_url, timeout=15, headers=self.opskins_headers)
        except requests.exceptions.Timeout:
            time.sleep(200)
            print "TIMEOUT EXCEPTION TRIGGERED"
            return -2

        print opsres.status_code
        elapsed = timeit.default_timer() - start_time
        print 'time at the request: ' + str(elapsed)
        self.trys_counter += 1

        if opsres.status_code == 503:
            print "the server started giving 503 na try ", self.trys_counter
            print "giving up now"
            return [-3, self.trys_counter]

        if self.trys_counter == 1000:
            self.trys_counter = 0
            time.sleep(300)
            print "sleeping for 5 mins!"

        price_total = 0
        
        start_time = timeit.default_timer()
        if opsres.status_code is 200:
            soup = BeautifulSoup(opsres.content,'lxml')
            items_bad = soup.find_all('div', {'class':'featured-item col-xs-12 col-sm-6 col-md-4 col-lg-3 center-block app_730_2'})
            if len(items_bad) == 0:
                print "For some reason i cound't scrape any items, maybe opskins is down.... "
                return -2

            list_ids_temp = []

            for item in items_bad:
                start_time_test = timeit.default_timer()

                json_good = False
                item_url = str(item.find('a',{'class':'market-name market-link'})['href'])
                item_OpId = re.findall(r'\d+', item_url)[0]
                item_name_no_condition = str(item.find('a',{'class':'market-name market-link'}).text.encode('utf-8')).strip()
                item_condition_temp = ' (' + str(item.find('small',{'class':'text-muted'}).text) + ')'
                item_name = item_name_no_condition+item_condition_temp

                elapsed_test = timeit.default_timer() - start_time_test
                print 'time elapsed at parsing html: ' + str(elapsed_test)

                #tenho que fazer decode('utf-8') do item_name_no_condition para verificar se este existe no dict da historia dos items
                start_time_test = timeit.default_timer()
                if item_OpId not in self.last_opsid_from_site:
                    if item_name.decode('utf-8') in self.item_price_history_sorted:
                        try:
                            try:
                                suggested_price_json = float(self.item_price_history_sorted[item_name.decode('utf-8')]['price']) / 100
                                json_good = True
                            except:
                                print "cant get price from json ABORT ABORT"
                            price = float((re.findall(r'\d+.\d+', item.find('div',{'class':'item-amount'}).text)[0]).replace(',',''))
                        except:
                            print 'Something went wrong getting the price of the item!'
                            print item.find('span',{'class':'market-name'}).text
                            print item.find('div',{'class':'item-amount'}).text
                            return -1
                        print 'Item:', item_name + ' | '+ str(item_OpId) +' | price:',price, ' sug price:', suggested_price_json, ' --> ' + str(suggested_price_json - price >= (0.15*suggested_price_json))
                        if json_good:
                            #if this item has a manual price enabled ill go down this path
                            if suggested_price_json - price >= (self.discount_percentage*suggested_price_json) and (price >= self.min_item_price and price <= 30):
                                items_to_email[item_name] = {'Suggested_price':suggested_price_json,
                                                            'Price': price,'Item_url': item_url, 'Opskins_id': item_OpId}
                                return_list.append(item_OpId)
                                price_total += price

                            elif suggested_price_json - price >= (self.discount_percentage*suggested_price_json) and price > 30:
                                items_to_email[item_name] = {'Suggested_price':suggested_price_json,
                                                            'Price': price,'Item_url': item_url, 'Opskins_id': item_OpId}
                                return_list.append(item_OpId)
                                price_total += price

                        else:
                            print self.item_price_history_sorted[item_name.decode('utf-8')]
                            print "not json good"

                elapsed_test = timeit.default_timer() - start_time_test
                print 'time elapsed checking if item is good: ' + str(elapsed_test)

                list_ids_temp.append(item_OpId)

            self.last_opsid_from_site = list_ids_temp

            if items_to_email:
                message = self.structure_email_message(items_to_email)
                if price_total <= self.opskins_balance:
                    try:
                        if self.send_email_bool:
                            self.send_email_new_item(self.FROM, self.TO, message, item_name)
                            print 'Sent email with the message:'
                            print message
                    except:
                        print "tried to send email with a newly found item but failed"

                    return_list.insert(0, 1)
                    return return_list
                else:
                    print "the stuff i found was to expensive for ya, please make more money"
                    print message
                    return 0
            else:
                print "Didn't get any new items to potencially buy!"
                elapsed_total = timeit.default_timer() - start_time
                print 'time after the request: ' + str(elapsed_total) + '\n\n'
                return 0

    #structures an email to be sent with the items found to be good to buy!
    def structure_email_message(self, items_dict):

        message = 'The following item(s) were found: \n'

        for item in items_dict:
            message += item + ': Suggested Price - ' + str(items_dict[item]['Suggested_price']) + \
                       ', Item price - ' + str(items_dict[item]['Price']) + \
                       ', Item url - https://opskins.com/index.php' + str(items_dict[item]['Item_url'])\
                       + ' Add to cart url: ' \
                         'https://opskins.com/ajax/shop_account.php?type=cart&param=add&id='+ \
                       str(items_dict[item]['Opskins_id']) + ' \n '

        return message


    def get_opskins_balance(self):

        res = requests.get("https://opskins.com/api/user_api.php?request=GetOP&key="+self.opskins_api_key)
        balance_temp = json.loads(res.content)
        self.opskins_balance = float(balance_temp['result']['op']) / 100
        return self.opskins_balance

    #reads the json file with all the items history info and sorts it by date.
    #the final result is hopefully a suggested price really accurate
    #if the item has a manual price, it gets it
    #else it gets the suggested price based on the last two days price history.
    def sort_prices(self, item_prices):
        count2 = 0
        temp_list2 = []
        for key_item in item_prices:
            if 'history' in item_prices[key_item]:
                item_prices[key_item] = eval(item_prices[key_item])
                history = item_prices[key_item]['history']
                temp_list = history.keys()
                temp_list = sorted(temp_list, key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), reverse=True)

                print item_prices[key_item]['name'].encode('utf-8')
                print str(item_prices[key_item]['price'])

                od = OrderedDict()
                for i in temp_list:
                    if i in history.keys():
                        od[i] = history[i]
                item_prices[key_item]['history'] = od

                counter =0
                temp_price = 0
                temp_count = 0
                for dates in item_prices[key_item]['history']:
                    if counter < 1:
                        temp_price += float(item_prices[key_item]['history'][dates]['price'])
                        temp_count += item_prices[key_item]['history'][dates]['count']
                        counter += 1
                if temp_count >= 6:
                    print 'temp price feito pela sort func: ', str(temp_price)
                    item_prices[key_item]['price'] = str(int(temp_price))
                    print 'preco que vai ser usado pelo bot: ', str(item_prices[key_item]['price'])
                    print '\n'
                else:
                    if "price" in item_prices[key_item]:
                        pass
                    else:
                        temp_list2.append(key_item)
                item_prices[key_item]["manual_price_bool"] = 0

        for item_temp in temp_list2:
            print "gone"
            item_prices.pop(item_temp)

        self.item_price_history_sorted = item_prices
        print len(self.item_price_history_sorted)
        return True


