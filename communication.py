#Author: Mike Jacobi !!!
#Virtual Mafia Game
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#This script has generic helper functions used by the Mafia server and clients

import os
import time
import threading
import random
from threading import Thread

pipeRoot='/home/moderator/pipes/'

logName=''
mLogName=''

conns=[]
allowed=[]

logChat=0
current=0

def complement(x,y):
    z=[]
    for val in y:
	if val not in x:
	    z.append(val)
    return z
	

def skip():
    global current,voteAllowDict
    voteAllowDict={'w':0,'W':0,'t':0}
    current=0

def sleep(duration):
    global current
    current=time.time()
    while time.time()<current+duration:
        time.sleep(1)

def setLogChat(n):
    global logChat
    logChat=n

def obscure():
    pass
    #while 1:
	#os.system('ls '+pipeRoot+'* > /dev/null 2> /dev/null')
#	time.sleep(.1)

def allow(pipes):
    global allowed
    allowed=pipes

notStop=1
def handleConnections(timeTillStart):
    global notStop
    possibleConnections=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    for c in possibleConnections:
        t=Thread(target=connect,args=[str(c)+'tos'])
        t.start()
    sleep(timeTillStart)
    notStop=0
    return conns

def connect(inputPipe):
    global notStop
    input=''
    while input!='connect' and notStop:
        try:
            input=recv(inputPipe)[2]
        except:
            pass
        if input=='connect':
            log(str(inputPipe)+' connected',1,0,1)
	    try:
		out='sto'+str(int(inputPipe[0]+inputPipe[1]))
	    except:
		out='sto'+inputPipe[0]
            send('Connected',out)
            conns.append(inputPipe)


def broadcast(msg, pipes):
    global logChat
    try:
        log(msg,1,logChat,1)
    except Exception, p:
	log('broadcast error:'+str(p),1,0,1)

    for pipe in pipes:
	try:
	    pipe='sto'+str(int(pipe[0]+pipe[1]))
	except:
        	pipe = 'sto'+pipe[0]
        try:
            send(msg,pipe)
        except Exception, p:
            log('broadcast error:'+str(p),1,0,1)
            

def send(msg, pipe):
    global allowed

    msg=msg.replace("'",'').replace('"','')

    try:
	try:
	    moniker=str(int(pipe[0]+pipe[1]))
	except:
       	    moniker=pipe[0]
        try:
            msg=msg.strip('\n')
        except:
            pass
        
        os.popen('echo "" > '+pipeRoot+pipe+'D/'+pipe).close()
        msg='(echo :'+moniker+':'+msg+' > '+pipeRoot+pipe+'D/'+pipe+') 2> /dev/null'
        o=os.popen(msg)
        o.read()
        o.close()
    except Exception, p:
        log('send error:'+str(p),1,0,1)

def recv(pipe):
    output=''
    while output=='':
        try:
            msg='(cat '+pipeRoot+str(pipe)+'D/'+str(pipe)+') 2> /dev/null'
            f=os.popen(msg)
            output=f.read().split('\n')
            f.close()

            for i in range(len(output)):
                if len(output[i])>0:
                    output[i]=output[i].split(':')
                    return output[i] 
        except Exception, p:
            log('receive error:'+str(p),1,0,1)


def log(msg, printBool,publicLogBool,moderatorLogBool):
    global logName,mLogName

    if publicLogBool:
	f=open(logName,'a')
    	f.write('('+str(int(time.time()))+')--'+msg+'\n')
	f.close()
    if moderatorLogBool:
	g=open(mLogName,'a')
	g.write('('+str(int(time.time()))+')--'+msg+'\n')
	g.close()
    if printBool:
        print msg

def setLogFileNames(passedLogName,passedMLogName):
    global logName, mLogName
    logName=passedLogName
    mLogName=passedMLogName

def clear(pipes):
    for p in pipes:
        for i in range(10):
            t=Thread(target=recv,args=[p])
            t.start()

def multiRecv(pipe, pipes,endTime):
    global allowed
    start = time.time()
    while 1:
	verified=1
        #if pipe in allowed:
        msg=recv(pipe)
	    #if msg==None:
		#continue
	    #if pipe.split('to')[0]==msg[1]:
		#verified=1
	    #else:
		#send('quit cheating!','sto'+pipe.split('to')[0])
		#continue
        #else:
            #time.sleep(1)
            #continue

        if verified and msg!=None and pipe in allowed:
            broadcast(msg[1]+'-'+msg[2], modPipes(pipe,allowed))
	else:
	    time.sleep(1)

def groupChat(pipes, endTime):
    for pipe in pipes:
        newPipes=modPipes(pipe, pipes)
        t = Thread(target=multiRecv,args=[pipe, newPipes, endTime])
        t.start()
        
#remove one pipe from pipes
def modPipes(pipe, pipes):
    newPipes=[]
    for p in pipes:
        if p!=pipe:
            newPipes.append(p)
    return newPipes

#this is a dictionary of booleans that forces only one group to vote at a time.
voteAllowDict={'w':0,'W':0,'t':0}
votes={}
votesReceived=0

def poll(pipes, votetime, validTargets, w, everyone):
    global votes,voteAllowDict,allowed,votesReceived,logChat
    votesReceived=0
    allowed=[]
    #broadcast('Time to vote.  Valid votes are '+str(validTargets), pipes)


    voteAllowDict={'w':0,'W':0,'t':0}
    voteAllowDict[w]=1

    voteThreads=[]
    votes={}
    for pipe in pipes:
        t = Thread(target=vote,args=[pipe, pipes, validTargets, w, everyone])
        voteThreads.append(t)
        voteThreads[-1].start()
    sleep(votetime+1)
    log(str(votes),1,logChat,1)

    winner=[]
    mode=0
    for v in votes.keys():
        if votes[v]>mode:
            mode=votes[v]
            winner=[v]
        elif votes[v]==mode:
            winner.append(v)
    return winner

def vote(pipe, pipes, validTargets, w, everyone):#w indicates which group is voting
    #everyone is used to broadcast, to hide the witch and wolves better.
    global votes,voteAllowDict,votesReceived

    try:
	client='sto'+str(int(pipe[0]+pipe[1]))
    except:
        client='sto'+pipe[0]
    while voteAllowDict[w]:
        i=recv(pipe)

        try:
            str(i[2])
        except Exception, p:
            continue 
        if voteAllowDict[w]==0:
            break
        try:
             if i[2] in validTargets:
                try:
                    votes[i[2]]+=1
                except Exception, p:
                    votes[i[2]]=1
                if w=='W':#capitol W is for 'witch'.  
                    broadcast('Witch voted.', everyone)
		    #skip()
		elif w=='w':#wolf stuff
		    broadcast(client+' voted for '+str(i[2]),pipes)
		    broadcast('Wolf vote received.',complement(pipes,everyone))	
                else:
                    broadcast(client+' voted for '+str(i[2]), pipes)

		votesReceived+=1
		if votesReceived==len(pipes):
		    skip()
                break
             else:
                send('invalid vote:'+str(i[2]),client)   
        except Exception, p:
	    print str(p)
            pass

def spawnDeathSpeech(pipe,all,endtime):
    t=Thread(target=deathSpeech,args=[pipe,all,endtime])
    t.start()
    sleep(endtime)
    t._Thread__stop()
    del(threading._active[t.ident])


def deathSpeech(pipe, all,endtime):
    broadcast(pipe+' is giving a deathspeech for '+str(endtime)+' seconds.',all)
    newPipes=modPipes(pipe,all)
    while 1:
        i=recv(pipe)
        try:
            broadcast(pipe+'-'+i[2],newPipes)
        except:
            pass

