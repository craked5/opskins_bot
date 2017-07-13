# OpSkins Bot!

################### THIS BOT IS NOW DEPRECATED. IT WILL NOT WORK ANYMORE #####################

Bot to buy things on Opskins skins based on the suggested price of the item (calculated by the bot, not the 7 days average).
Only works on Unix systems right now!
You will also need the client side Chrome Extension that buys things.
It can be found here: https://github.com/craked5/opsbot_extension

First things first you need to add stuff to the config file.
The following stuff in the config file needs to be configured:

- email_username: email used to send messages with items found. (ONLY SUPPORTS GMAIL!!!!!!!!!!!!!!)
- email_password: above email password
- send_to_email: the email that you want to send the messages to, can be the same as the above
- opskins_api_key: your api key for the website Opskins.com (go to account settings to get it!)
- redis_server: the ip of the redis server you are using to store the prices (MANDATORY!)
- bitskins_api_key: your api key for Bitskins. Only useful if you want to get the prices there.
- bitskins_secret: your bitskins secret. see above.
- send_email: true or false, if you want to send an email after it buys something! (ONLY GMAIL!!!!!!!!!!!!!!!!!!)
- discount_percentage: the percentage of discount that the item has to have in order to be bought! Ex: 30 or 24.5
- min_item_price: minimum price that the item has to have in order to be bought! Ex: 3 or 5.67
- server_ip: the local ip that is going to run the bot server, normally 0.0.0.0
- using_redis: true or false, if you want to use redis as storage! I highly encourage this!

Now that you configured the bot, run the opskins_prices.py script to get a list of all the suggested sell prices that will be used in the bot! It will take some time since you are getting a lot of items from the Opskins api and they limit the time between requests. I recommend you to run this script once a day!

After thats finished, you run server.py and then run the extension. You will see feedback on the server and after a while it will start looking for things to buy!

If you have any questions just post it on the issues and i'll try to awswer it as fast as i can!

I did not profit from this, this was merely an exercise!
