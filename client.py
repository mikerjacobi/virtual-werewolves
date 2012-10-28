#Author: Mike Jacobi
#Virtual Mafia Game
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#This is an example client for players to connect to the Mafia server

import signal
import sys
import os
import pwd
sys.path.append('/home/moderator/')
import communication as c
from threading import Thread

uid=pwd.getpwuid(os.getuid())[0].split('p')[1]
inPipe='sto'+uid
outPipe=uid+'tos'


def listen():
	isListening=1
	sendThread = Thread(target=send,args=[])
	sendThread.setDaemon(True)
	sendThread.start()

	while isListening:
		try: data=c.recv(inPipe)#receive data from moderator
		except:continue
		try:#process received data
			if data[2]=="close":
				print "Connection closed."
				isListening=0
				sendThread._Thread__stop()
				exit()
			else: print data[2]
		except Exception, p: pass

def send():
    c.send('connect',outPipe)
    while 1:
		try: 
			msg=raw_input()#listen for user input
			c.send(msg,outPipe)
		except: pass

if __name__=='__main__':
	listen()
