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

id=pwd.getpwuid(os.getuid())[0].split('p')[1]
inPipe='sto'+id
outPipe=id+'tos'


def listen():
    isListening=1

    sendThread = Thread(target=send,args=[])
    sendThread.start()

    voteRecv=0

    while isListening:

	try:
        	data=c.recv(inPipe)#receive data from moderator
	except:
		continue

        try:#process received data
            if data[2]=="close":
                print "You have been killed."
		isListening=0
		sendThread._Thread__stop()
		exit()
                #x=os.kill(os.getpid(),signal.SIGKILL)
            elif data[2]=='win':
                print 'You win!'
		sendThread._Thread__stop()
                isListening=0
		exit()
                #x=os.kill(os.getpid(),signal.SIGKILL)
            else:# len(data)>0:
                print data[2]
	
        except Exception, p:
	    #print 'listenerror:'+str(p)
	    pass

def send():
    #print 'Type "connect" to play!'
    c.send('connect',outPipe)
    while 1:
	try: 
		msg=raw_input()#listen for user input
		c.send(msg,outPipe)
	except: pass


if __name__=='__main__':
	listen()

