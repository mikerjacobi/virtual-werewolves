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

all=[]

pipeRoot='/home/moderator/pipes/'

logName=''
mLogName=''

conns=[]
allowed=[]

logChat=0
current=0

readVulnerability=1
imposterMode=1
isSilent=1
def setVars(passedReadVulnerability, passedImposterMode):
    #descriptions of these variables can be seen in the mafia.config file
    global readVulnerability, imposterMode
    readVulnerability=int(passedReadVulnerability)
    imposterMode=int(passedImposterMode)


def complement(x,y):
    z=[]
    for val in y:
	if val not in x:
	    z.append(val)
    return z
	

def skip():
    global current,voteAllowDict, deathspeech, deadGuy, voters, targets
    #voteAllowDict={'w':0,'W':0,'t':0}
    current=0
    deathspeech=0
    deadGuy=""
    voters=[]
    targets=[]

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
	#time.sleep(.1)

def allow(pipes):
    global allowed
    allowed=pipes

notStop=1
def handleConnections(timeTillStart):
    global notStop, all
    possibleConnections=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    for c in possibleConnections:
        t=Thread(target=connect,args=[str(c)+'tos'])
	#allowed.append(str(c)+'tos')
        t.start()
    sleep(int(timeTillStart))
    notStop=0
    all=conns
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
            send('You are connected.  Please wait for the game to start.',out)
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
        
        #os.popen('echo "" > '+pipeRoot+pipe+'D/'+pipe).close()
        msg='(echo :'+moniker+':'+msg+' > '+pipeRoot+pipe+'D/'+pipe+') 2> /dev/null'
        o=os.popen(msg)
        o.read()
        o.close()
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
		    try:
            		moniker=str(int(pipe[0]+pipe[1]))
        	    except:
	            	moniker=pipe[0]

		    if (output[i][1]=='s' or output[i][1]==moniker or imposterMode==1):
                    	return output[i] 
        except Exception, p:
            #log('receive error:'+str(p),0,0,0)
	    pass


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

deathspeech=0
deadGuy=""
def multiRecv(pipe, pipes,endTime):
    global allowed, voters, targets, deathspeech, deadGuy, all
    start = time.time()
    while 1:
	verified=1
        msg=recv(pipe)

	#if someones giving a deathspeech
	if verified and deathspeech and pipe==deadGuy:
		broadcast(msg[1]+'-'+msg[2], modPipes(pipe,all))

	#if were voting
	elif verified and msg!=None and votetime and pipe in voters:
		vote(pipe,msg[2])
	
	#if its open chat
        elif verified and msg!=None and pipe in allowed:
            broadcast(msg[1]+'-'+msg[2], modPipes(pipe,allowed))

	#otherwise prevent spam
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
votetime=0
voteAllowDict={'w':0,'W':0,'t':0}
votes={}
votesReceived=0
voters=[]
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
    #0 - result=victim; 1 - vote not unan; 2 - vote is tie
    resultType=0
	
    if int(isUnanimous) and mode!=len(passedVoters): #the voteCount of the winner is not equal the number of voters
	resultType=1
    elif len(results)>1 or len(results)==0:
	resultType=2

    validTargets=[]
    votetime=0
    voters=[]    

    return results,resultType

def vote(voter, target):
        global votes,votesReceived,voters,targets,character,isSilent

	respondToVoter='sto'+voter.split('to')[0]

	if target in targets:
		try:
			votes[target]+=1
		except:
			votes[target]=1

		#message[0] is sent to who[0]; 1 to 1; etc.
		messages=[]
		who=[]

		log(voter+" voted for "+target,1,0,1)

		if character=="witch":
			messages.append("Witch voted")
			who.append(all)
			#broadcast("Witch voted",all)
		elif character=="wolf":
			if isSilent:
				messages.append(voter+' voted.')
			else:
				messages.append(voter+' voted for '+target)
			who.append(voters)

			messages.append("Wolf vote received.")
			who.append(complement(voters,all))
		else:#townsperson vote
			if isSilent:
				messages.append(voter+' voted.')
			else:
				messages.append(voter+' voted for '+target)
			who.append(all)

		for i in range(len(messages)):
			broadcast(messages[i],who[i])

		votesReceived+=1
		if votesReceived==len(voters):
			skip()
	else:
		send('invalid vote: '+target,respondToVoter)

def spawnDeathSpeech(pipe,all,endtime):
    global deathspeech, deadGuy
    deathspeech=1
    deadGuy=pipe

    sleep(endtime)

    deathspeech=0
    deadGuy=""


