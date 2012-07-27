#Author: Mike Jacobi
#Test and Update: Xu Zhang
#Virtual Werewolf Game
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#This is an example client for players to connect to the Mafia server

#Copyright (c) 2012 Mike Jacobi, Xu Zhang, Roya Ensafi, Jed Crandall
#This file is part of Virtual Werewolf Game.

#Virtual werewolf is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#Virtual werewolf is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with Virtual werewolf.  If not, see <http://www.gnu.org/licenses/>.

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

#c.allow([inPipe,outPipe])

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






