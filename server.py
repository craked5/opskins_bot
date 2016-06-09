#!/usr/bin/env python
# -*- coding: utf-8 -*-
#async_mode = "gevent"

#if async_mode == 'gevent':
    #from gevent import monkey
    #.patch_all()

from flask import Flask
from flask_socketio import SocketIO
from bot_logic import mainLogic
import time
from threading import Thread
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
socketio = SocketIO(app, engineio_logger = True, allow_upgrades = True, ping_timeout = 80000, ping_interval=15)
thread = None
exit_signal = False
thread_exited = False

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

def background_thread():
    global exit_signal
    global thread_exited
    print "THREAD HAS BEEN INICIATED!"

    while True:
        print 'exit signal: ' + str(exit_signal)
        if exit_signal == True:
            thread_exited = True
            print "thread exiting"
            return 0
        print 'The check recent process has begun!'
        return_temp = ms.check_recent_opskins()
        if type(return_temp) == type([]):
            return_temp.pop(0)
            msg = ''
            for i in return_temp:
                msg += str(i)+','
            msg = msg[:-1]
            print msg
            socketio.emit('buy_list', str(msg))
            thread_exited = True
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

def start_thread():
    global exit_signal
    global thread_exited
    global thread

    if thread_exited is True:
        exit_signal = False
        thread_exited = False
        thread = None

    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = False
        thread.start()

@socketio.on('connect')
def connect():
    print "Client has connected!"

@socketio.on('ready')
def readybuy(data):
    print "the client sent a ready signal so im starting the bot again!"
    print data
    time.sleep(4)
    ms.get_opskins_balance()
    start_thread()

@socketio.on('disconnect')
def disconnect():
    global exit_signal
    global thread_exited
    exit_signal = True

    while thread_exited is False:
        print 'thread_exited: ' + str(thread_exited)
        time.sleep(1)
        print "WAITING FOR THE CHECK RECENT THREAD TO STOP!"
        pass

    socketio.emit("bot_stopped", str({'stopped':"The bot was stopped successfully"}))
    print('disconnected from client!')

@socketio.on('start_bot')
def start_bot(data):
    print data
    start_thread()
    if thread is not None:
        socketio.emit("bot_started", str({'started':"The bot was started successfully"}))
    else:
        socketio.emit("bot_started_false", str({'started':"The bot was not started successfully"}))

@socketio.on('stop_bot')
def stop_bot(data):
    print "STOPING BOT NOW!"
    global exit_signal
    global thread_exited
    exit_signal = True

    while thread_exited is False:
        time.sleep(1)
        print "WAITING FOR THE CHECK RECENT THREAD TO STOP!"

    print "BOT IS NOW STOPPED!"
    socketio.emit("bot_stopped", str({'stopped':"The bot was stopped successfully"}))

@socketio.on('opskins_balance')
def opskins_balance(data):
    print data
    socketio.emit("opskins_balance", str(ms.get_opskins_balance()))

if __name__ == '__main__':
    socketio.run(app)