#!/usr/bin/env python
# -*- coding: utf-8 -*-
async_mode = "gevent"

if async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from flask import Flask
from flask_socketio import SocketIO
from bot_logic import mainLogic
import time
from threading import Thread
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, engineio_logger = True, allow_upgrades = True, async_mode=async_mode, ping_timeout = 80000, ping_interval=15)
thread = None
exit_signal = False
process_ended = False

def background_thread():
    global exit_signal

    while True:
        print 'Beggining of the check recent items process!'
        print 'exit signal: ' + str(exit_signal)
        if exit_signal == True:
            print "Check recent process ending"
            return 0
        print 'The process has begun!'
        return_temp = ms.check_recent_opskins()
        if type(return_temp) == type([]):
            return_temp.pop(0)
            msg = ''
            for i in return_temp:
                msg += str(i)+','
            msg = msg[:-1]
            print msg
            socketio.emit('buy_list', str(msg))
            return True
        else:
            if return_temp == 0:
                ms.logger.info("Didn't get anything or the items didnt change, continuing....")
            elif return_temp == -1:
                ms.logger.warn('Failed on getting the price/suggested price, continuing....')
            elif return_temp == -2:
                ms.logger.warn("For some reason i cound't scrape any items, maybe opskins is down.... ")
            elif return_temp[0] == -3:
                ms.logger.warn("server started giving 503 na try " + str(return_temp[1]))
                break

            #time.sleep(random.uniform(1,2))

@socketio.on('connect')
def connect():
    print "client has connected to the server!"

@socketio.on('ready')
def readybuy(data):
    print "the client sent a ready signal so im starting a new search"
    time.sleep(4)
    ms.get_opskins_balance()
    print data

@socketio.on('disconnect')
def disconnect():
    global exit_signal
    global process_ended
    exit_signal = True
    while process_ended is False:
        print process_ended
        time.sleep(1)
        print "WAITING FOR THE RECENT CHECKING PROCESS TO END"
        pass
    print('disconnected from client!')

@socketio.on('start')
def start():
    background_thread()
    socketio.emit('started', str({"started":"the bot has started"}))




if __name__ == '__main__':
    ms = mainLogic()
    try:
        balance = ms.get_opskins_balance()
        print 'opskins balance: ' + str(balance)
    except:
        print "cant get opskins balance"
    if ms.send_email_bool:
        ms.start_smtp(ms.email_username, ms.email_password)
        print 'Connected to email server'
    else:
        print "Not going to send emails"
    socketio.run(app, host=ms.server_ip, port=80)