import json
import unicodedata
from datetime import datetime, timedelta
import requests

with open("utils/csgodoubleitems.json") as csgodoublefile:
    csgodoubleitems = json.load(csgodoublefile)

res = requests.get("https://opskins.com/pricelist/730.json")
opsdict = json.loads(res.content)

#with open("utils/opskinsall.json") as opskinsall:
#    opsdict = json.load(opskinsall)


opskinsitems = {}
for key in opsdict:
    checked = False
    yesterday = datetime.now() - timedelta(days=1)
    while checked is not True:
        for date in opsdict[key]:
            if date == yesterday.strftime("%Y-%m-%d"):
                new_key = key.replace(u"\u2122", '')
                new_key = unicodedata.normalize('NFKD', new_key).encode('ascii', 'ignore').lstrip()
                opskinsitems[new_key] = opsdict[key][date]
                opskinsitems[new_key]["price"] = float(opsdict[key][date]["price"])
                checked = True
                continue
        yesterday = yesterday - timedelta(days=1)

used_items = []
for key in opskinsitems:
    for index, item in enumerate(csgodoubleitems["items"]):
        if key == csgodoubleitems["items"][index]["name"]:
            if key not in used_items:
                used_items.append(key)
                if (((float(csgodoubleitems["items"][index]["price"]) / 1000) / (float(opskinsitems[key]["price"] / 100))) - 1) * 100 >= float(45):
                    print key
                    print "Preco do CSGODOUBLE: " + str(float(csgodoubleitems["items"][index]["price"]) / 1000)
                    try:
                        print "Preco do OPSKINS: " + str(float(opskinsitems[key]["price"] / 100))
                        print (((float(csgodoubleitems["items"][index]["price"]) / 1000) / (float(opskinsitems[key]["price"] / 100))) - 1) * 100
                        print "\n"
                    except KeyError:
                        print "ERRO AO OBTER PRECO NO OPSKINS"