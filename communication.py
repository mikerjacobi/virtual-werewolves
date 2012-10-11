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
    #descriptions of these variables can be seen in the mafia.config file
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
    #possibleConnections=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

    if randomize:
            f=open('names.txt','r').read().split('\n')[0:-1]
            for i in range(len(f)):
                    r=random.randint(0,len(f)-1)
                    temp=f[i]
                    f[i]=f[r]
                    f[r]=temp

    for conn in range(1,16):#possibleConnections:
	if randomize:
		name=f[conn]
	else:
		name='group'+str(conn)
		
        t=Thread(target=connect,args=[str(conn),str(name)])
        t.start()
    sleep(int(timeTillStart))
    isHandlingConnections=0
    all=conns
    return conns

def connect(num,name):
    global isHandlingConnections

    inPipe=num+'tos'
    outPipe='sto'+num

    connInput=''
    while connInput!='connect' and isHandlingConnections:
        try: connInput=recv(inPipe)[2]
	except Exception, p: pass

        if connInput=='connect':
            log(name+' connected',1,0,1)
            send('Hello, '+name+'.  You are connected.  Please wait for the game to start.',outPipe)
	    conns[name]=[inPipe,outPipe]


def broadcast(msg, players):
    global logChat
    log(msg,1,logChat,1)

    for player in players.keys():
	try: send(msg,players[player][1])
        except Exception, p: log('broadcast error:'+str(p),1,0,1)
            

def send(msg, pipe):
    msg=msg.replace("'",'').replace('"','').replace('\n','')

    try:
	out=pipe.split('to')[0]
        msg='(echo :'+out+':'+msg+' > '+pipeRoot+pipe+'D/'+pipe+') 2> /dev/null &'
        o=os.popen(msg)
    except Exception, p:
        log('send error:'+str(p),1,0,1)

def recv(pipe):
	global readVulnerability, imposterMode
        try:
	    if readVulnerability==0:
	    	f=open(pipeRoot+str(pipe)+'D/'+str(pipe),'r')
	    	output=f.read().split('\n')
	    	f.close()
	    else:
		msg='(cat '+pipeRoot+str(pipe)+'D/'+str(pipe)+') 2> /dev/null'
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
            #log('receive error:'+str(p),0,0,0)
	    pass


#print, publicLog, modLog
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

def clear(pipes):
    for p in pipes:
        for i in range(10):
            t=Thread(target=recv,args=[p])
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
		broadcast(msg[1]+'-'+msg[2], modPlayers(player,all))

	#if were voting
	elif votetime and player in voters.keys():
		vote(player,msg[2])
	
	#if its open chat
        elif player in allowed:
            broadcast(msg[1]+'-'+msg[2], modPlayers(player,allowed))

	#otherwise prevent spam
	else:
	    time.sleep(1)

def groupChat(players):
    for player in players.keys():
        newPlayers=modPlayers(player, players)
        t = Thread(target=multiRecv,args=[player, newPlayers])
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
			if isSilent: messages.append(voter+' voted.')
			else: messages.append(voter+' voted for '+target)
			who.append(voters)

			messages.append("Wolf vote received.")
			who.append(complement(voters,all))
		else:#townsperson vote
			if isSilent: messages.append(voter+' voted.')
			else: messages.append(voter+' voted for '+target)
			who.append(all)

		for i in range(len(messages)):
			broadcast(messages[i],who[i])

		votesReceived+=1
		if votesReceived==len(voters): skip()

	else:
		send('invalid vote: '+target, voters[voter][1])

def spawnDeathSpeech(player,endtime):
    global deathspeech, deadGuy
    deathspeech=1
    deadGuy=player

    sleep(endtime)

    deathspeech=0
    deadGuy=""


