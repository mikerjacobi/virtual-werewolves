#Author: Mike Jacobi !!!
#Virtual Werewolves
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#This script has generic helper functions used by the Mafia server and clients

import os
import time
import threading
import random
from threading import Thread

all={}

pipeRoot='/home/moderator/pipes/'
logName=''
mLogName=''
conns={}
allowed={}
logChat=0
currentTime=0

readVulnerability=1
imposterMode=1
isSilent=1
def setVars(passedReadVulnerability, passedImposterMode, publicLogName, moderatorLogName):
    #descriptions of these variables can be seen in the config file
    global readVulnerability, imposterMode, logName,mLogName
    readVulnerability=int(passedReadVulnerability)
    imposterMode=int(passedImposterMode)
    logName=publicLogName
    mLogName=moderatorLogName


#returns all elements in y that are not in x
def complement(x,y):
    z={}
    for element in y.keys():
	if element not in x.keys(): z[element]=y[element]
    return z
	
#resets all variables 
def skip():
    global currentTime,deathspeech, deadGuy, voters, targets
    currentTime=0
    deathspeech=0
    deadGuy=""
    voters={}
    targets={}

def sleep(duration):
    global currentTime
    currentTime=time.time()
    while time.time()<currentTime+duration:
        time.sleep(1)

def setLogChat(n):
    global logChat
    logChat=n

def obscure():
    pass
    #while 1:
	#os.system('ls '+pipeRoot+'* > /dev/null 2> /dev/null')
	#time.sleep(.1)

def allow(players):
    global allowed
    allowed=players

isHandlingConnections=1
def handleConnections(timeTillStart, randomize):
    global isHandlingConnections, all

    f=open('names.txt','r').read().split('\n')[0:-1]
    if randomize: random.shuffle(f)

    for conn in range(1,len(f)):
	if randomize: name=f[conn]
	else: name='group%s'%(str(conn))
		
        t=Thread(target=connect,args=[str(conn),str(name)])
	t.setDaemon(True)
        t.start()

    sleep(int(timeTillStart))
    isHandlingConnections=0
    all=conns
    return conns

def connect(num,name):
	#global isHandlingConnections

	inPipe='%stos'%num
	outPipe='sto%s'%num
	duration=.1

	connected=False
	connInput=''
	try:
		while not connected:#connInput!='connect':
			try: connInput=recv(inPipe)[2]
			except Exception, p: pass

			if connInput=='connect' and isHandlingConnections:
				log('%s connected'%name,1,0,1)
				send('Hello, %s.  You are connected.  Please wait for the game to start.'%name,outPipe)
				conns[name]=[inPipe,outPipe]
				connected=True
			elif not isHandlingConnections:
				duration=1
				send('Game already started.  Please wait for next game.',outPipe)
				send('close',outPipe)
			time.sleep(duration)
	except:
		pass


def broadcast(msg, players):
	global logChat
	log(msg,1,logChat,1)
	
	time.sleep(.1)

	for player in players.keys():
		try:
			send(msg,players[player][1])
		except Exception, p: pass#log('broadcast error:%s'%p,1,0,1)
            

def send(msg, pipe):
    msg=msg.replace("'",'').replace('"','').replace('\n','').replace('(','[').replace(')',']').replace('>','').replace('<','').replace(':','')

    try:
	sender=pipe.split('to')[0]
	#f=open(pipeRoot+pipe+'D/'+pipe,'w')
	#f.write(':'+sender+':'+msg+'\n')
	#f.close()
	if len(msg)!=0:	
		msg='(echo :%s:%s > %s%sD/%s) 2> /dev/null &'%(sender,msg,pipeRoot,pipe,pipe)
		o=os.popen(msg)
    except Exception, p:
		pass
        #log('send error:%s'%p,1,0,1)

def recv(pipe):
   	global readVulnerability, imposterMode
        try:
	    if readVulnerability==0:
		f=open('%s%sD/%s'%(pipeRoot,pipe,pipe),'r')
	    else:
		msg='(cat %s%sD/%s)2>/dev/null'%(pipeRoot,pipe,pipe)
           	f=os.popen(msg)
            output=f.read().split('\n')
            f.close()		
	  
            for i in range(len(output)):
                if len(output[i])>0:
                    output[i]=output[i].split(':')
		    out=pipe.split('to')[0]
		    if (output[i][1]=='s' or output[i][1]==out or imposterMode==1):
                    	return output[i] 
        except Exception, p:
            log('receive error:%s'%p,0,0,0)
	    pass


#print, publicLog, modLog
def log(msg, printBool,publicLogBool,moderatorLogBool):
    global logName,mLogName

    if printBool:
	print msg

    msg='(%s) - %s\n'%(str(int(time.time())),msg)
    if publicLogBool:
	f=open(logName,'a')
    	f.write(msg)
	f.close()
    if moderatorLogBool:
	g=open(mLogName,'a')
	g.write(msg)
	g.close()

def clear(pipes):
    for p in pipes:
        for i in range(10):
            t=Thread(target=recv,args=[p])
	    t.setDaemon(True)
            t.start()

deathspeech=0
deadGuy=""
def multiRecv(player, players):
    global allowed, voters, targets, deathspeech, deadGuy, all

    while 1:
        msg=recv(all[player][0])
	if msg==None: continue

	#if someones giving a deathspeech
	if deathspeech and player==deadGuy:
	    broadcast('%s-%s'%(player,msg[2]),modPlayers(player,all))

	#if were voting
	elif votetime and player in voters.keys():
	    vote(player,msg[2])
	
	#if its group chat
        elif player in allowed:
	    broadcast('%s-%s'%(player,msg[2]), modPlayers(player,allowed))

	#otherwise prevent spam
	else:
	    time.sleep(1)

def groupChat(players):
    for player in players.keys():
        newPlayers=modPlayers(player, players)
        t = Thread(target=multiRecv,args=[player, newPlayers])
	t.setDaemon(True)
        t.start()
        
#remove one pipe from pipes
def modPlayers(player, players):
    newPlayers={}
    for p in players.keys():
        if p!=player:
            newPlayers[p]=players[p]
    return newPlayers

#voteAllowDict is a dictionary of booleans that forces only one group to vote at a time.
votetime=0
voteAllowDict={'w':0,'W':0,'t':0}
votes={}
votesReceived=0
voters={}
targets=[]
character=""
def poll(passedVoters, duration, passedValidTargets, passedCharacter, everyone, isUnanimous, passedIsSilent):
    global votes,voteAllowDict,allowed,votesReceived,logChat,votetime,voters,targets, character, isSilent
	
    votetime=1
    voters=passedVoters
    votesReceived=0
    votes={}
    targets=passedValidTargets
    character=passedCharacter
    isSilent=passedIsSilent

    sleep(duration+1)
    log(str(votes),1,logChat,1)

    results=[]
    mode=0
    for v in votes.keys():
        if votes[v]>mode:
            mode=votes[v]
            results=[v]
        elif votes[v]==mode:
            results.append(v)

    #this var signifies the class of result
    #0 - results[0]=victim; 1 - vote not unan; 2 - vote is tie
    resultType=0
	
    if int(isUnanimous) and mode!=len(passedVoters): #the voteCount of the winner is not equal the number of voters
	resultType=1
    elif len(results)>1 or len(results)==0:#tie or nonvote
	resultType=2

    validTargets=[]
    votetime=0
    voters={}   

    return results,resultType

def vote(voter, target):
    global votes,votesReceived,voters,character,isSilent

    if target in targets:
	try: votes[target]+=1
	except: votes[target]=1
	#message[0] is sent to who[0]; message[1] sent to who[1]; etc.
	messages=[]
	who=[]

	log(voter+" voted for "+target,1,0,1)

	if character=="witch":
	    messages.append("Witch voted")
	    who.append(all)
	elif character=="wolf":
	    if isSilent: messages.append('%s voted.'%voter)
	    else: messages.append('%s voted for %s'%(voter,target))
	    who.append(voters)

   	    messages.append("Wolf vote received.")
	    who.append(complement(voters,all))
	else:#townsperson vote
	    if isSilent: messages.append('%s voted.'%voter)
	    else: messages.append('%s voted for %s'%(voter,target))
	    who.append(all)

	for i in range(len(messages)):
	    broadcast(messages[i],who[i])

	votesReceived+=1
	if votesReceived==len(voters): skip()

    else:
	send('invalid vote: %s'%target, voters[voter][1])

def spawnDeathSpeech(player,endtime):
    global deathspeech, deadGuy
    deathspeech=1
    deadGuy=player

    sleep(endtime)

    deathspeech=0
    deadGuy=""


