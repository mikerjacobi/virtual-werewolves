#Author: Mike Jacobi
#Virtual Mafia Game
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#This is an example client for players to connect to the Mafia server

import signal
import sys
import os
sys.path.append('/home/moderator/')
import communication as c
from threading import Thread

p = os.popen('whoami')#get user name
id=p.readline().strip('\n').split('p')[1]
p.close()

inPipe='sto'+id
outPipe=id+'tos'

def listen():
    listenCheck=1

    sendThread = Thread(target=send,args=[])
    sendThread.start()

    voteRecv=0

    while listenCheck:
	try:
        	o=c.recv(inPipe)#receive data from moderator
	except:
		continue
        try:#process received data
            if o[2]=="close":
                print "You have been killed."
                listenCheck=0
                x=os.kill(os.getpid(),signal.SIGKILL)
            elif o[2]=='win':
                print 'You win!'
                listenCheck=0
                x=os.kill(os.getpid(),signal.SIGKILL)
            elif len(o)>0:
                print o[2]
        except Exception, p:
	    #print 'listenerror:'+str(p)
	    pass

def send():
    #print 'Type "connect" to play!'
    c.send('connect',outPipe)
    while 1:
        msg=raw_input()#listen for user input
        c.send(msg,outPipe)

listen()

def quit(Signal, frame):
    print 'please dont force quit...'
signal.signal(signal.SIGINT,quit)






