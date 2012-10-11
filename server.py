#Author: Mike Jacobi
#Virtual Mafia Game
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#server.py is the automated moderator for Mafia

import datetime
import sys
import os
import time
import random
import signal
import communication as c
from threading import Thread

i={}
inputVars=open('mafia.config','r').read().split('\n')
for var in inputVars:
	var=var.strip('\n').split('=')
	key=var[0]
	try:#if a line doesn't have an = sign
		value=var[1]
	except:
		continue
	i[key]=value
logFile=''

#time parameters
timeTillStart=int(i['timeTillStart'])
wolftalktime=int(i['wolfTalkTime'])
wolfvotetime=int(i['wolfVoteTime'])
townvotetime=int(i['townVoteTime'])
towntalktime=int(i['townTalkTime'])
witchvotetime=int(i['witchVoteTime'])
deathspeechtime=int(i['deathSpeechTime'])

test=int(i['test'])
numWolves=int(i['numWolves'])
start = time.time()

#group people by roles
all={}
wolves={}
townspeople={}
witch={}

potions=[int(i['kill']),int(i['heal'])]#[kill,heal]

round=1

def removePlayer(player,giveSpeech):
    global all, wolves, witch
    isTownsperson=1
   
    newAll={}
    for p in all.keys():
        if player!=p:
            newAll[p]=all[p]
    newWolves={}
    for p in wolves.keys():
        if player!=p:
            newWolves[p]=wolves[p]
        else:
            #c.broadcast(player+' was a wolf!',all)
	    c.log(p+'-wolf killed.',1,0,1)
            isTownsperson=0
    if player in witch.keys():
        #c.broadcast(player+' was the witch!',all)
	c.log(player+'-witch killed',1,0,1)
        witch={}
        isTownsperson=0
    if isTownsperson:
	pass
        #c.broadcast(player+' was a townsperson.',all)
	c.log(player+'-townsperson killed',1,0,1)
    if giveSpeech:
        c.broadcast('These are '+player+'s last words.', all)
	c.send("Share your parting words.", all[player][1])
	c.setLogChat(1)
        c.spawnDeathSpeech(player,deathspeechtime)
	c.setLogChat(0)
    else:
	c.broadcast(player+' was eliminated by the moderator.',all)

    c.send('close',all[player][1])
    all=newAll
    wolves=newWolves
    if len(wolves)==1:
	wolftalktime=0

def quitGame(Signal, frame):
    global all
    c.broadcast('close',all)
    c.log('\nGAME FORCE QUIT BY MODERATOR',1,1,1)
    os.system('chmod 744 log/*m.log 2> /dev/null')
    msg='Game is over.'
    if not test:
    	os.system('echo "'+msg+'" | wall')
    #os.system('killall -s 9 cat')
    #os.system('killall -s 9 sh 2> /dev/null')
    os.kill(os.getpid(),signal.SIGKILL)
signal.signal(signal.SIGINT, quitGame)

def assign():
    global all, wolves, witch
    #balance the game accordingly
    numPlayers = len(all.keys())

    config=['W']
    for i in range(numWolves):
	config.append('w')
    for i in range(numPlayers-numWolves-1):
	config.append('t')

    #randomize roles
    for i in range(numPlayers):
        swap = random.randint(0,numPlayers-1)
        temp = config[i]
        config[i]=config[swap]
        config[swap]=temp

    #assign roles and inform players
    for i in range(len(all.keys())):
	player=all.keys()[i]

        if config[i]=='w':
            wolves[player]=all[player]
            role='wolf'
        elif config[i]=='W':
            witch[player]=all[player]
            townspeople[player]=all[player]
            role='witch'
        else:
            townspeople[player]=all[player]
            role='townsperson'
	try:
        	c.send('~~~~~ YOU ARE A '+role+' ~~~~~', all[player][1])
	except Exception, p:
		c.log('ASSIGNERROR:'+str(p),1,0,1)

 
def standardTurn():
    global all, witch, potions
    wolfkill=0
    witchkill=0
    
    try:
        c.broadcast("Night falls and the town sleeps.  Everyone close your eyes",all)
	c.log('Night',0,1,0)
        #time.sleep(1)


        #**************WEREWOLVES************************
        c.broadcast("Werewolves, open your eyes.", c.complement(wolves,all))
	c.broadcast('Werewolves, '+str(wolves.keys())+', you must choose a victim.  You have '+str(wolftalktime)+' seconds to discuss.' ,wolves)
	c.log('Werewolves debate',0,1,0)
        c.allow(wolves)
        c.sleep(wolftalktime)

	c.broadcast("Werewolves, vote.", c.complement(wolves,all))
	
		

	c.broadcast('Werewolves, you must vote on a victim to eat.  You have '+str(wolfvotetime)+' seconds to vote.  Valid votes are '+str(sorted(all.keys())),wolves)
	c.log('Werewolves vote',0,1,0)
        wolfvote,t=c.poll(wolves,wolfvotetime, all.keys(), 'wolf', all, i['wolfUnanimous'],i['wolfSilentVote'])
	c.broadcast('Werewolves, go to sleep.',c.complement(wolves,all))
	if t==1:
	    c.broadcast('Vote not unanimous, nobody eaten.', wolves)
	    c.log('Werewolves not unanimous',0,1,0)
        #elif len(wolfvote)!=1:
	elif t==2:
            c.broadcast('Tie', wolves)
	    c.log('Werewolves vote tie',0,1,0)
        elif t==0:
            msg="Werewolves, you selected to eat "+str(wolfvote[0])
            wolfkill=1
            c.broadcast(msg,wolves)
	    c.log('Werewolves selected '+str(wolfvote[0]),0,1,0)

        #**********END WEREWOLVES************************


        #**************WITCH************************
        #construct the witch's options
        if len(witch)>0 and (potions[0] or potions[1]):
            c.broadcast('Witch, open your eyes.',c.complement(witch,all))
	    c.log('Witch vote',0,1,0)
	    witchPlayer=witch[witch.keys()[0]]

            if wolfkill:
                validKills=[]
                for p in all:
                    if p!=wolfvote[0]:
                        validKills.append(p)
                if potions[0] and potions[1]:
                    witchmoves=validKills+['Heal','Pass']
                elif potions[0]:
                    witchmoves=validKills+['Pass']
                else:
                    witchmoves=['Heal','Pass']
		c.send('Witch, wake up.  The wolves killed '+str(wolfvote)+'.  Valid votes are '+str(sorted(witchmoves)),witchPlayer[1])
            else:
                if potions[0]:
                    witchmoves=all.keys()+['Pass']
                else:
                    witchmoves=['Pass']
		c.send('Witch, the wolves didnt feed tonight.  Valid votes are '+str(sorted(witchmoves)),witchPlayer[1])

            #witch voting
            witchVote,t=c.poll(witch,witchvotetime,witchmoves,'witch',all,0,0)

            if witchVote==[] or witchVote[0]=='Pass' or t:
		c.log('Witch passed',1,1,1)
		c.broadcast('Witch, close your eyes',all)
            elif witchVote[0]=='Heal':
		c.send('The Witch healed you!',all[wolfvote[0]][1])
		c.log('The Witch healed '+wolfvote[0]+'!',0,0,1)
                wolfkill=0
                potions[1]-=1
		c.broadcast('The witch used a health potion! '+str(potions[1])+' heal(s) remaining.',all)
            else:
                witchkill=1
                potions[0]-=1
	        c.broadcast('Witch, close your eyes',all)
        #**************END WITCH************************

        #**************START TOWN***********************
        if wolfkill:
            c.broadcast('The werewolves ate '+str(wolfvote[0])+'!',all)
	    c.log('Werewolves killed '+wolfvote[0],0,1,0)
            removePlayer(wolfvote[0],1)
            if len(wolves)==0 or len(all)==len(wolves):
                return 1
        if witchkill:
            c.broadcast('The Witch poisoned '+witchVote[0]+'!  '+ str(potions[0])+' poison(s) remaining.',all)
	    c.log('Witch poisoned '+witchVote[0],0,1,0)
            removePlayer(witchVote[0],1)
            if len(all)-len(wolves)==0 or len(wolves)==0:
                return 1

        c.allow(all)
	c.setLogChat(1)
        c.broadcast('It is day.  Everyone, open your eyes.  You will have '+str(towntalktime)+' seconds to discuss who the werewolves are.',all)
	c.log('Day-townspeople debate',0,1,0)
        c.sleep(towntalktime)
        c.allow({})

	c.log('Townspeople vote',0,1,0)
	c.broadcast('Townspeople, you have '+str(townvotetime)+' seconds to cast your votes on who to hang. Valid votes are '+str(sorted(all.keys())), all)
        killedPlayer,t = c.poll(all, townvotetime, all.keys(), 'town', all,i['townUnanimous'],i['townSilentVote'])
        #if len(killedPlayer)!=1:
	if t==2:
            msg = 'The vote resulted in a tie between players '+str(killedPlayer)+', so nobody dies today.'
            c.broadcast(msg, all)
	    c.log('Townspeople vote tie',0,1,0)
        elif t==1:
		c.broadcast('The vote was not unanimous',all)
		c.log('Townspeople vote not unanimous',0,1,0)
	else:
            c.broadcast('The town voted to hang '+str(killedPlayer[0])+'!',all)
	    c.log('Townspeople killed '+str(killedPlayer[0]),0,1,0)
            removePlayer(killedPlayer[0],1)
	c.setLogChat(0)
        #******************END TOWN*******************
        return 1
    except Exception, error:
        c.log('STANDARDTURNERROR:'+str(error),1,0,1)
        return 0

def listenerThread():
    global round,all
    while 1:
        i=raw_input().strip('\n')
	if i=='':
	    pass
        elif i=='help':
	    os.system('cat moderatorHelp.txt')
        elif i=='status':
	    print 'round '+str(round)
            print 'all: '+str(all.keys())
            print 'wolves: '+str(wolves.keys())

            wStatus=': '
            wStatus+=str(potions[0])+' poisons, '
            wStatus+=str(potions[1])+' heals '
            print 'witch: '+str(witch.keys())+wStatus
        elif i[0:4]=='kill':
            player=i.split(' ')[1]
            c.broadcast('Moderator removed '+player,all)
	    c.log('Moderator removed '+player,0,1,0)
            removePlayer(player,0)
	elif i=='skip':
	    c.skip()
	    #c.broadcast('Moderator skipped current section.',all)
	    c.log('Moderator skipped current section.',0,1,0)
	else:
	    c.broadcast('moderator-'+i,all)
	    #c.log('moderator-'+i,0)

def main():
    global all,round

    if test:
	publicLogName='log/dummy.log'
	moderatorLogName='log/dummy-m.log'
	next=9999
    else:
    	nextround=open('log/nextround','r')
    	next=int(nextround.readline().strip('\n'))
    	nextround.close()
    	nextround=open('log/nextround','w')
   	nextround.write(str(next+1))
   	nextround.close()
    	msg='Game '+str(next)+' starts in '+str(timeTillStart)+' seconds.'
	os.system('echo "'+msg+'" | wall')
    	publicLogName='log/'+str(next)+'.log'
        moderatorLogName='log/'+str(next)+'m.log'

    #pass the necessary input variables into the communication script
    c.setVars(i['readVulnerability'],i['imposterMode'],publicLogName,moderatorLogName)

    if i['moderatorLogMode']==1:
	os.system('touch '+moderatorLogName)
	os.system('chmod 700 '+moderatorLogName)
    else:
    	os.system('cp log/template '+moderatorLogName)

    c.log('GAME: '+str(next),1,1,1)

    t=Thread(target=listenerThread,args=[])
    t.start()
    c.log('\nmoderator listener thread started',1,0,1)

    all=c.handleConnections(timeTillStart,int(i['randomizeNames']))

    #ot=Thread(target=c.obscure,args=[])
    #ot.start()
    #c.log('obscurity thread started',1,0,1)

    #assign each connection a role
    assign()
    c.log('roles assigned',1,0,1)

    u=Thread(target=c.groupChat,args=[all,])
    u.start()
    c.log('group chat thread started',1,0,1)

    c.log('\nBegin.',1,1,1)
    c.broadcast('There are '+str(len(wolves))+' wolves, and '+str(len(all)-len(wolves))+' townspeople.',all)
    c.allow({})

    #the main part of the game
    while len(wolves)!=0 and len(wolves)<len(all):
	    c.log('\n\n',1,1,1)
	    c.broadcast('*'*50,all)
	    c.broadcast('*'*21+'ROUND '+str(round)+'*'*22,all)
	    c.broadcast('*'*15+str(len(all))+' players remain.'+'*'*18,all)
	    c.broadcast('*'*50,all)
	    c.log('Round '+str(round),0,1,0)
	    c.log('Townspeople: '+str(all.keys()),1,1,1)
	    c.log('Werewolves: '+str(wolves.keys()),1,0,1)
	    c.log('Witch: '+str(witch.keys()),1,0,1)
	    round+=1
            standardTurn()


    #end game
    if len(wolves)==0:
        c.log('\nTownspeople win!',0,1,0)
        c.broadcast('Townspeople win!',all)
    elif len(wolves)==len(all):
        c.log('\nWerewolves win!',0,1,0)
        c.broadcast('Werewolves win!',all)
    c.broadcast('win',all)

    c.log('End',1,1,1)
    if not test: os.system('chmod 744 log/'+str(next)+'m.log')
    #logFile.close()
    msg='Game '+str(next)+' is over.'
    if not test:
        os.system('echo "'+msg+'" | wall')
    os.system('killall -s 9 cat 2> /dev/null')
    os.system('killall -s 9 sh 2> /dev/null')
    os.kill(os.getpid(),signal.SIGKILL)

main()
