import redis
import json
import unicodedata
from datetime import datetime, timedelta
import requests

url = "http://02ovn7g99m-dsn.algolia.net/1/indexes/GameItem/query?x-algolia-api-key=" \
      "01f041b8b83806ce1ebd7878d0fce8be&x-algolia-application-id=02OVN7G99M&x-algolia-" \
      "agent=Algolia%20for%20vanilla%20JavaScript%203.10.2"
headers = {
    "accept": "application/json",
    "Accept - Encoding": "gzip,deflate",
    "Accept - Language":"pt-PT,pt;,q = 0.8,en-US;q=0.6,en;q=0.4,fr;q=0.2,es;q=0.2",
    "Cache - Control":"no-cache",
    "Connection":"keep-alive",
    "Content - Length":"136",
    "content - type":"application/x-www-form-urlencoded",
    "DNT":"1",
    "Host":"02ovn7g99m-dsn.algolia.net",
    "Origin":"http://csgowild.com",
    "Pragma":"no-cache",
    "Referer":"http://csgowild.com/store",
    "User - Agent": "Mozilla / 5.0(WindowsNT10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 49.0.2623.110 Safari / 537.36"
}
data = {
    "params":"query=*&page=0&distinct=2&facets=*&attributesToRetr"
             "ieve=*&numericFilters=ruby_purchase_price%20%3C%205000000&hitsPerPage=200"
}
res = requests.post(url, json=data, headers=headers)
csgowilditems = json.loads(res.content)

resops = requests.get("https://opskins.com/pricelist/730.json")
opsdict = json.loads(resops.content)

#GET OPSKINS PRICES FROM REDIS AND COMPARE PRICES-----------------------------------------------
used_items = []
opskinsitems = {}
for key in opsdict:
    checked = False
    yesterday = datetime.now() - timedelta(days=1)
    while checked is not True:
        for date in opsdict[key]:
            if date == yesterday.strftime("%Y-%m-%d"):
                opskinsitems[key] = opsdict[key][date]
                opskinsitems[key]["price"] = float(opsdict[key][date]["price"])
                checked = True
                continue
        yesterday = yesterday - timedelta(days=1)

for key in opskinsitems:
    for index, item in enumerate(csgowilditems["hits"]):
        if key == csgowilditems["hits"][index]["name"]:
            if key not in used_items:
                used_items.append(key)
                print csgowilditems["hits"][index]["ruby_purchase_price"]
                print opskinsitems[key]["price"]
                if (((float(csgowilditems["hits"][index]["ruby_purchase_price"]) / 1000) / (float(opskinsitems[key]["price"] / 100))) - 1) * 100 >= float(45):
                    print key
                    print "Preco do CSGOWILD: " + str(float(csgowilditems["hits"][index]["ruby_purchase_price"]) / 1000)
                    try:
                        print "Preco do OPSKINS: " + str(float(opskinsitems[key]["price"] / 100))
                        print (((float(csgowilditems["hits"][index]["ruby_purchase_price"]) / 1000) / (float(opskinsitems[key]["price"] / 100))) - 1) * 100
                        print "\n"
                    except KeyError:
                        print "ERRO AO OBTER PRECO NO OPSKINS"


