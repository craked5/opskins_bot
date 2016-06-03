# OpSkins Bot!

Bot to buy things on Opskins skins based on the suggested price of the item (calculated by the bot, not the 7 days average).
Only works on Unix systems right now!
You will also need the client side Chrome Extension that buys things.
It can be found here: https://github.com/craked5/opsbot_extension

First things first you need to add stuff to the config file.
The following stuff in the config file needs to be configured:

- email_username: email used to send messages with items found. (ONLY SUPPORTS GMAIL!!!!!!!!!!!!!!)
- email_password: aboves email password
- send_to_email: the email that you want to send the messages to, can be the same as the above
- opskins_api_key: your api key for the website Opskins.com (go to account settings to get it!)
- redis_server: the ip of the redis server you are using to store the prices (MANDATORY!)
- bitskins_api_key: your api key for Bitskins. Only useful if you want to get the prices there.
- bitskins_secret: your bitskins secret. see above.

Now that you configured the bot, run the items_history.py script to get a list of all the suggested sell prices that will be used in the bot! (IT MAY TAKE A WHILE!!)

After thats finished, you run server.py and then run the extension. You will see feedback on the server and after a while it will start looking for things to buy!
