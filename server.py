#Virtual Werewolf Game
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012
#server.py is the automated moderator for Mafia

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

import datetime
import sys
import os
import time
import random
import signal
import communication as c
from threading import Thread

logFile=''

#time parameters
timeTillStart=60
wolftalktime=120
wolfvotetime=60
townvotetime=60
towntalktime=240
witchvotetime=60
deathspeechtime=60
test=0

#test time params
#timeTillStart=20
#wolftalktime=60
#wolfvotetime=60
#townvotetime=60
#towntalktime=60
#witchvotetime=60
#deathspeechtime=20


start = time.time()

#group people by roles
all=[]
wolves=[]
townspeople=[]
witch=[]

potions=[1,1]#[kill,heal]

round=1


def removePlayer(player,giveSpeech):
    global all, wolves, witch,wolftalktime
    isTownsperson=1
   
    newAll=[]
    for p in all:
        if player!=p:
            newAll.append(p)
    newWolves=[]
    for p in wolves:
        if player!=p:
            newWolves.append(p)
        else:
            #c.broadcast(player+' was a wolf!',all)
	    c.log(p+'-wolf killed.',1,0,1)
            isTownsperson=0
    if player in witch:
        #c.broadcast(player+' was the witch!',all)
	c.log(player+'-witch killed',1,0,1)
        witch=[]
        isTownsperson=0
    if isTownsperson:
	pass
        #c.broadcast(player+' was a townsperson.',all)
	c.log(player+'-townsperson killed',1,0,1)
    if giveSpeech:
        c.broadcast('These are '+player+'s last words.', c.complement(player,all))
	p='sto'+player[0]
	try:
		int(player[1])
		p+=player[1]
	except:
		pass
	c.send("Share your parting words.", p)
	c.setLogChat(1)
        c.spawnDeathSpeech(player,all,deathspeechtime)
	c.setLogChat(0)
    else:
	c.broadcast(player+' was eliminated by the moderator.',all)
    all=newAll
    wolves=newWolves
    if len(wolves)==1:
	wolftalktime=0
    try:
	out='sto'+str(int(player[0]+player[1]))
    except:
	out='sto'+player[0]
    c.send('close',out)

def quitGame(Signal, frame):
    global all
    c.broadcast('close',all)
    c.log('\nGAME FORCE QUIT BY MODERATOR',1,1,1)
    os.system('chmod 744 log/*m.log')
    msg='Game is over.'
    if not test:
    	os.system('echo "'+msg+'" | wall')
    os.system('killall -s 9 cat')
    os.system('killall -s 9 sh')
    os.kill(os.getpid(),signal.SIGKILL)
signal.signal(signal.SIGINT, quitGame)

def assign(all):
    #balance the game accordingly
    numPlayers = len(all)
    try:
        config = open('config/'+str(numPlayers)+'.txt','r').read().strip('\n').split(',')
    except:
        print "Cant play with "+str(numPlayers)+" people.  Quitting."
        return 1
    #randomize roles
    for i in range(numPlayers):
        swap = random.randint(0,numPlayers-1)
        temp = config[i]
        config[i]=config[swap]
        config[swap]=temp
    #assign roles and inform players
    for i in range(len(all)):
        player = all[i]
	try:
	    pipe='sto'+str(int(player[0]+player[1]))
	except Exception, p:
  	    pipe = 'sto'+player[0]
        if config[i]=='w':
            wolves.append(player)
            role='wolf'
        elif config[i]=='W':
            witch.append(player)
            townspeople.append(player)
            role='witch'
        else:
            townspeople.append(player)
            role='townsperson'
	try:
        	c.send('~~~~~ YOU ARE A '+role+' ~~~~~', pipe)
	except Exception, p:
		c.log('ASSIGNERROR:'+str(p),1,0,1)

 
def standardTurn():
    global all, witch, potions
    wolfkill=0
    witchkill=0
    
    try:
        c.broadcast("Night falls and the town sleeps.  Everyone close your eyes",all)
	c.log('Night',0,1,0)
        time.sleep(1)


        #**************WEREWOLVES************************
        c.broadcast("Werewolves, open your eyes.", c.complement(wolves,all))
	c.broadcast('Werewolves, '+str(wolves)+', you must choose a victim.  You have '+str(wolftalktime)+' seconds to discuss.' ,wolves)
	c.log('Werewolves debate',0,1,0)
        c.allow(wolves)
        c.sleep(wolftalktime)

	c.broadcast("Werewolves, vote.", c.complement(wolves,all))
	c.broadcast('Werewolves, you must vote on a victim to eat.  You have '+str(wolfvotetime)+' to vote.  Valid votes are '+str(all),wolves)
	c.log('Werewolves vote',0,1,0)
        wolfvote = c.poll(wolves,wolfvotetime, all, 'wolf', all)
	c.broadcast('Werewolves, go to sleep.',c.complement(wolves,all))
        if len(wolfvote)!=1:
            c.broadcast('Tie', wolves)
	    c.log('Werewolves vote tie',0,1,0)
        else:
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
	    try:
		witchPlayer='sto'+str(int(witch[0][0]+witch[0][1]))
	    except:
		witchPlayer='sto'+witch[0][0]
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
		c.send('Witch, wake up.  The wolves killed '+str(wolfvote)+'.  Valid votes are '+str(witchmoves),witchPlayer)
            else:
                if potions[0]:
                    witchmoves=all+['Pass']
                else:
                    witchmoves=['Pass']
		c.send('Witch, the wolves didnt feed tonight.  Valid votes are '+str(witchmoves),witchPlayer)

            #witch voting
            witchVote=c.poll(witch,witchvotetime,witchmoves,'witch',all)
            nonwitch=[]
            for p in all:
                if p!=witch[0]:
                    nonwitch.append(p)
            c.clear(nonwitch)#clear queued chat messages

            print 'wv:'+str(witchVote)
            if witchVote==[] or witchVote[0]=='Pass':
		c.log('Witch passed',1,1,1)
		c.broadcast('Witch, close your eyes',all)
            elif witchVote[0]=='Heal':
                c.broadcast('The witch used the health potion!',all)
		c.send('The witch healed you!',wolfvote[0])
		c.log('Witch healed '+wolfvote[0],0,0,1)
                wolfkill=0
                potions[1]=0
            else:
                witchkill=1
                potions[0]=0
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
            c.broadcast('The witch used the poison on '+witchVote[0]+'!',all)
	    c.log('Witch poisoned '+witchVote[0],0,1,0)
            removePlayer(witchVote[0],1)
            if len(all)-len(wolves)==0 or len(wolves)==0:
                return 1

        c.allow(all)
	c.setLogChat(1)
        c.broadcast('It is day.  Everyone, open your eyes.  You will have '+str(towntalktime)+' seconds to discuss who the werewolves are.',all)
	c.log('Day-townspeople debate',0,1,0)
        c.sleep(towntalktime)
        c.allow([])

	c.log('Townspeople vote',0,1,0)
	c.broadcast('Townspeople, you have '+str(townvotetime)+' seconds to cast your votes on who to hang. Valid votes are '+str(all), all)
        killedPlayer = c.poll(all, townvotetime, all, 'town', all)
        if len(killedPlayer)!=1:
            msg = 'The vote resulted in a tie between players: '+str(killedPlayer)+', so nobody dies today.'
            c.broadcast(msg, all)
	    c.log('Townspeople vote tie',0,1,0)
        else:
            c.broadcast('The town voted to hang '+str(killedPlayer[0])+'!',all)
	    c.log('Townspeople killed '+str(killedPlayer[0]),0,1,0)
            removePlayer(killedPlayer[0],1)
	c.setLogChat(0)
        #******************END TOWN*******************
        return 1
    except Exception, p:
        c.log('STANDARDTURNERROR:'+str(p),1,0,1)
        return 0

def listenerThread():
    global round
    while 1:
        i=raw_input().strip('\n')
	if i=='':
	    pass
        elif i=='help':
	    os.system('cat config/moderatorHelp.txt')
        elif i=='status':
	    print 'round '+str(round)
            print 'all: '+str(all)
            print 'wolves: '+str(wolves)

            wStatus=', '
            if potions[0]:
                wStatus+='poison '
            if potions[1]:
                wStatus+='health '
            print 'witch: '+str(witch)+wStatus
        elif i[0:4]=='kill':
            player=i.split(' ')[1]
            c.broadcast('Moderator removed '+player,all)
	    c.log('Moderator removed '+player,0,1,0)
            removePlayer(player,0)
	elif i=='skip':
	    c.skip()
	    c.broadcast('Moderator skipped current section.',all)
	    c.log('Moderator skipped current section.',0,1,0)
	else:
	    c.broadcast('moderator-'+i,all)
	    #c.log('moderator-'+i,0)

def main():
    global all,round


    nextround=open('log/nextround','r')
    next=int(nextround.readline().strip('\n'))
    nextround.close()
    nextround=open('log/nextround','w')
    nextround.write(str(next+1))
    nextround.close()

    msg='Game '+str(next)+' starts in '+str(timeTillStart)+' seconds.'
    if not test:
	os.system('echo "'+msg+'" | wall')

    if test:
	name='log/dummy.log'
	moderatorLogName='log/dummyM.log'
    else:
    	name='log/'+str(next)+'.log'
        moderatorLogName='log/'+str(next)+'m.log'
    #logFile=open(name,'w')
    c.setLogFileNames(name,moderatorLogName)
    os.system('touch '+moderatorLogName)
    os.system('chmod 700 '+moderatorLogName)
    c.log('GAME: '+str(next),1,1,1)

    t=Thread(target=listenerThread,args=[])
    t.start()
    c.log('\nmoderator listener thread started',1,0,1)

    all=c.handleConnections(timeTillStart)

    '''
    inc=5
    while (timeTillStart-(time.time()-start))>0:
        tts=int(timeTillStart-(time.time()-start))
        if tts==3:
            inc=1
        if tts%inc==0 and tts!=0: 
            c.broadcast('game starts in '+str(tts)+'s', all)
            time.sleep(1) 
    '''
    #c.sleep(timeTillStart)

    #ot=Thread(target=c.obscure,args=[])
    #ot.start()
    #c.log('obscurity thread started',1,0,1)

    #assign each connection a role
    assign(all)
    c.log('roles assigned',1,0,1)

    u=Thread(target=c.groupChat,args=[all,0])
    u.start()
    c.log('group chat thread started',1,0,1)

    c.log('\nBegin.',1,1,1)
    c.broadcast('There are '+str(len(wolves))+' wolves, and '+str(len(all)-len(wolves))+' townspeople.',all)

    c.allow([])


    #the main part of the game
    while len(wolves)!=0 and len(wolves)<len(all):
	    c.log('\n\n',1,1,1)
	    c.broadcast('*'*50,all)
	    c.broadcast('*'*21+'ROUND '+str(round)+'*'*21,all)
	    c.broadcast('*'*15+str(len(all))+' players remain.'+'*'*15,all)
	    c.broadcast('*'*50,all)
	    c.log('Round '+str(round),0,1,0)
	    c.log('Townspeople: '+str(all),1,1,1)
	    c.log('Werewolves: '+str(wolves),1,0,1)
	    c.log('Witch: '+str(witch),1,0,1)
	    round+=1
            standardTurn()


    #end game
    if len(wolves)==0:
        c.log('\nTownspeople win!',0,1,0)
        c.broadcast('Townspeople win!',all)
    elif len(wolves)==len(all):
        c.log('\nWerewolves win!',0,1,0)
        c.broadcast('Werewolves win!',all)
    c.broadcast('close',all)

    c.log('End',1,1,1)
    os.system('chmod 744 log/'+str(next)+'m.log')
    #logFile.close()
    msg='Game '+str(next)+' is over.'
    if not test:
        os.system('echo "'+msg+'" | wall')
    os.system('killall -s 9 cat')
    os.system('killall -s 9 sh')
    os.kill(os.getpid(),signal.SIGKILL)

main()
