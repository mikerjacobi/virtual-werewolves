#Author: Mike Jacobi
#Test and Update: Xu Zhang
#Virtual Werewolves
#Collaborators: Roya Ensafi, Jed Crandall
#server.py is the automated moderator for Virtual Werewolves

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

import traceback
import datetime
import sys
import os
import time
import random
import signal
import communication as c
import threading
from threading import Thread

i={}
inputVars=open('config','r').read().split('\n')
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
giveDeathSpeech=int(i['deathSpeech'])
numWolves=int(i['numWolves'])

#moderator assignment global vars
wolfChoose=int(i['wolfChoose'])
moderatorAssignment=0
moderatorAssignmentContinue=0
moderatorAssignmentList=[]

#group people by roles
all={}
wolves={}
townspeople={}
witch={}

potions=[int(i['kill']),int(i['heal'])]#[kill,heal]

round=1

def removePlayer(player):
 	global all, wolves, witch
	isTownsperson=1
   
	newAll={}
	for p in all.keys():
		if player!=p: newAll[p]=all[p]
	newWolves={}
	for p in wolves.keys():
		if player!=p: newWolves[p]=wolves[p]
		c.log('%s-wolf killed.'%p,1,0,1)
		isTownsperson=0
	if player in witch.keys():
		c.log('%s-witch killed'%player,1,0,1)
		witch={}
		isTownsperson=0
	if isTownsperson:
		c.log('%s-townsperson killed'%player,1,0,1)
	c.setLogChat(1)
	if giveDeathSpeech:
		c.broadcast('These are %ss last words.'%player, all)
		c.send("Share your parting words.", all[player][1])
		c.spawnDeathSpeech(player,deathspeechtime)
	c.setLogChat(0)

	c.send('close',all[player][1])
	all=newAll
	wolves=newWolves
	if len(wolves)<=1: wolftalktime=0

gameNumber=9999
winner='No winner'
def quitGame(Signal, frame):
    global all, winner, gameNumber
    c.broadcast('close',all)
    c.log('\nGAME FORCE QUIT BY MODERATOR',1,1,1)
    os.chmod(moderatorLogName,0744)
    if not test: os.system('echo "Game %d is over.  %s.  Please reconnect your client to play again." | wall'%(gameNumber,winner))
    for t in threading.enumerate():
		try: t._Thread__stop()
		except: pass
    sys.exit()

signal.signal(signal.SIGINT, quitGame)

def assign():
	global all, wolves, witch,moderatorAssignment,moderatorAssignmentContinue,moderatorAssignmentList,moderatorAssignmentChoices
	numPlayers = len(all.keys())

	if not wolfChoose: #randomly assign roles
		config=['W']
		for i in range(numWolves): config.append('w')
		for i in range(numPlayers-numWolves-1): config.append('t')

    	#randomize roles
		random.shuffle(config)

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
			c.send('~~~~~ YOU ARE A %s ~~~~~'%role, all[player][1])
	else: #moderator chooses roles
		moderatorAssignment=1
		print '\nModerator Assignment:'
		moderatorAssignmentChoices=all.keys()
		print 'Choose wolves from %s. enter "done" when finished.'%str(sorted(moderatorAssignmentChoices))
		moderatorAssignmentContinue=1
		while moderatorAssignmentContinue==1:
			time.sleep(1)
		wolfList=moderatorAssignmentList
		moderatorAssignmentList=[]	

		moderatorAssignmentChoices=[]
		for p in all.keys():
			if p not in wolfList: moderatorAssignmentChoices.append(p)
		print 'Choose witch from %s.'%str(sorted(moderatorAssignmentChoices))
		moderatorAssignmentContinue=1
		while moderatorAssignmentContinue==1:
			if len(moderatorAssignmentList)==1: 
				if moderatorAssignmentList[0] in wolfList:
					moderatorAssignmentList=[]
				else: break
			else: time.sleep(.1)
		witchList=moderatorAssignmentList
		moderatorAssignment=0

		for player in all.keys():
			if player in witchList:
				witch[player]=all[player]
				role='witch'
			elif player in wolfList:
				wolves[player]=all[player]
				role='wolf'
			else: #player is a townsperson
				townspeople[player]=all[player]
				role='townsperson'
			c.send('~~~~~ YOU ARE A %s ~~~~~'%role, all[player][1])



def standardTurn():
	global all, witch, potions, towntalktime,wolftalktime
	wolfkill=0
	witchkill=0
	try:
		c.broadcast("Night falls and the town sleeps.  Everyone close your eyes",all)
		c.log('Night',0,1,0)

        #**************WEREWOLVES************************
		if len(wolves)<2: wolftalktime=0
		c.broadcast("Werewolves, open your eyes.", c.complement(wolves,all))
		c.broadcast('Werewolves, %s, you must choose a victim.  You have %d seconds to discuss.  Possible victims are %s'%(str(wolves.keys()),wolftalktime, str(sorted(all.keys()))) ,wolves)
		c.log('Werewolves debate',0,1,0)
		c.allow(wolves)
		c.sleep(wolftalktime)
		c.broadcast("Werewolves, vote.", c.complement(wolves,all))
		c.broadcast('Werewolves, you must vote on a victim to eat.  You have %d seconds to vote.  Valid votes are %s.'%(wolfvotetime, str(sorted(all.keys()))),wolves)
		c.log('Werewolves vote',0,1,0)
		wolfvote,voteType=c.poll(wolves,wolfvotetime, all.keys(), 'wolf', all, i['wolfUnanimous'],i['wolfSilentVote'])
		c.broadcast('Werewolves, go to sleep.',c.complement(wolves,all))
	
		if voteType==1:
			c.broadcast('Vote not unanimous, nobody eaten.', wolves)
			c.log('Werewolves not unanimous',0,1,0)
		elif voteType==2:
			c.broadcast('Tie', wolves)
			c.log('Werewolves vote tie',0,1,0)
		elif voteType==0:
			msg="Werewolves, you selected to eat %s"%str(wolfvote[0])
			wolfkill=1
			c.broadcast(msg,wolves)
			c.log('Werewolves selected %s'%str(wolfvote[0]),0,1,0)
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
				validKills=sorted(validKills)
				if potions[0] and potions[1]:
					witchmoves=validKills+['Heal','Pass']
				elif potions[0]:
					witchmoves=validKills+['Pass']
				else:
					witchmoves=['Heal','Pass']
				c.send('Witch, wake up.  The wolves killed %s.  Valid votes are %s.'%(str(wolfvote),str(witchmoves)),witchPlayer[1])
			else:
				if potions[0]:
					witchmoves=sorted(all.keys())+['Pass']
				else:
					witchmoves=['Pass']
				c.send('Witch, the wolves didnt feed tonight.  Valid votes are %s'%str(witchmoves),witchPlayer[1])

            #witch voting
			if len(witchmoves)>1:
				witchVote,voteType=c.poll(witch,witchvotetime,witchmoves,'witch',all,0,0)
			else:
				witchVote=[]
				voteType=9999

			if witchVote==[] or witchVote[0]=='Pass' or voteType!=0:
				c.log('Witch passed',1,1,1)
				c.broadcast('Witch, close your eyes',all)
			elif witchVote[0]=='Heal':
				c.send('The Witch healed you!',all[wolfvote[0]][1])
				c.log('The Witch healed %s!'%wolfvote[0],0,0,1)
				wolfkill=0
				potions[1]-=1
				c.broadcast('The witch used a health potion! %d heal[s] remaining.'%potions[1],all)
		#c.broadcast('The witch used a health potion! '+str(potions[1])+' heal[s] remaining.',all)
			else:
				witchkill=1
				potions[0]-=1
				c.broadcast('Witch, close your eyes',all)
        #**************END WITCH************************
        #**************START TOWN***********************
		if wolfkill:
			c.broadcast('The werewolves ate %s!'%wolfvote[0],all)
			c.log('Werewolves killed %s'%wolfvote[0],0,1,0)
			removePlayer(wolfvote[0])

		if len(wolves)==0 or len(all)==len(wolves):
			return 1
        
		if witchkill:
			c.broadcast('The Witch poisoned %s!  %d poison[s] remaining.'%(witchVote[0],potions[0]),all)
			c.log('Witch poisoned %s'%witchVote[0],0,1,0)
			removePlayer(witchVote[0])

		if len(all)-len(wolves)==0 or len(wolves)==0:
			return 1

        
		c.allow(all)
		c.setLogChat(1)
		if len(all)==2: towntalktime=0
		c.broadcast('It is day.  Everyone, %s, open your eyes.  You will have %d seconds to discuss who the werewolves are.'%(str(sorted(all.keys())),towntalktime),all)
		c.log('Day-townspeople debate',0,1,0)
		c.sleep(towntalktime)
		c.allow({})
		c.log('Townspeople vote',0,1,0)
		c.broadcast('Townspeople, you have %d seconds to cast your votes on who to hang. Valid votes are %s'%(townvotetime,str(sorted(all.keys()))), all)

		killedPlayer,voteType = c.poll(all, townvotetime, all.keys(), 'town', all,i['townUnanimous'],i['townSilentVote'])
		if voteType==2:
			msg = 'The vote resulted in a tie between players %s, so nobody dies today.'%killedPlayer
			c.broadcast(msg, all)
			c.log('Townspeople vote tie',0,1,0)
		elif voteType==1:
			c.broadcast('The vote was not unanimous',all)
			c.log('Townspeople vote not unanimous',0,1,0)
		else:
			c.broadcast('The town voted to hang %s!'%killedPlayer[0],all)
			c.log('Townspeople killed %s'%str(killedPlayer[0]),0,1,0)
			removePlayer(killedPlayer[0])
			c.setLogChat(0)
        #******************END TOWN*******************
		return 1
	except Exception, error:
		c.log('STANDARDTURNERROR:%s'%str(error),1,0,1)
		return 0

def listenerThread():
    global round,all,moderatorAssignment,moderatorAssignmentContinue,moderatorAssignmentList,moderatorAssignmentChoices
    while 1:
	try: i=raw_input().strip('\n')
	except: break
	if i=='':
		pass
	elif moderatorAssignment==1: #handle moderator assignment
		if i=='done':
			moderatorAssignmentContinue=0
		elif i in moderatorAssignmentChoices and i not in moderatorAssignmentList:
			moderatorAssignmentList.append(i)
			print 'added %s'%i
		else:
			print 'invalid.'
	elif i=='help':
		#x=s.Popen(['ls','-l'],stdout=s.PIPE).communicate()[0].split('\n')
		os.system('cat moderatorHelp.txt')
	elif i=='status':
		print 'round %d'%round
		print 'all: %s'%str(all.keys())
		print 'wolves: %s'%str(wolves.keys())
		wStatus=': '
		wStatus+='%d poisons, '%potions[0]
		wStatus+='%d heals '%potions[1]
		print 'witch: %s%s'%(str(witch.keys()),wStatus)
	elif i[0:4]=='kill':
		player=i.split(' ')[1]
		c.broadcast('Moderator removed %s'%player,all)
		c.log('Moderator removed %s'%player,0,1,0)
		removePlayer(player)
	elif i=='skip':
	    c.skip()
	    #c.broadcast('Moderator skipped current section.',all)
	    c.log('Moderator skipped current section.',0,1,0)
	else:
		audience=i.split(' ')[0]
		if audience=='all': c.broadcast('moderator to all-%s'%i[4:],all)
		elif audience=='wolves': c.broadcast('moderator to wolves-%s'%i[7:],wolves)
		elif audience=='witch': c.broadcast('moderator to witch-%s'%i[6:],witch)
		else: print '***Start your message with "all", "wolves", or "witch". ***'

	time.sleep(.1)

publicLogName=''
moderatorLogName=''
listenThread=None
chatThread=None

def main():
    global all,round,publicLogName,moderatorLogName, winner,gameNumber

    if test:
	publicLogName='log/dummy.log'
	moderatorLogName='log/dummy-m.log'
	os.chmod(moderatorLogName, 0700)
	gameNumber=9999
    else:
    	nextround=open('log/nextround','r')
    	gameNumber=int(nextround.readline().strip('\n'))
    	nextround.close()
    	nextround=open('log/nextround','w')
   	nextround.write(str(gameNumber+1))
   	nextround.close()
	msg='Game %d starts in %d seconds.'%(gameNumber,timeTillStart)
    	#msg='Game '+str(next)+' starts in '+str(timeTillStart)+' seconds.'
	os.system('echo "%s" | wall'%msg)
    	publicLogName='log/%d.log'%gameNumber
        moderatorLogName='log/%dm.log'%gameNumber
	
    	if i['moderatorLogMode']==1:
	    os.system('touch '+moderatorLogName)
	    os.system('chmod 700 '+moderatorLogName)
    	else:
    	    os.system('cp log/template '+moderatorLogName)

	

    #pass the necessary input variables into the communication script
    c.setVars(i['readVulnerability'],i['imposterMode'],publicLogName,moderatorLogName)

    c.log('GAME: %d'%gameNumber,1,1,1)

    listenThread=Thread(target=listenerThread,args=[])
    listenThread.setDaemon(True)
    listenThread.start()
    c.log('\nmoderator listener thread started',1,0,1)

    all=c.handleConnections(timeTillStart,int(i['randomizeNames']))

    #ot=Thread(target=c.obscure,args=[])
    #ot.start()
    #c.log('obscurity thread started',1,0,1)

    #assign each connection a role
    assign()
    c.log('roles assigned',1,0,1)

    chatThread=Thread(target=c.groupChat,args=[all,])
    chatThread.setDaemon(True)
    chatThread.start()
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
    if len(wolves)==0: winner='Townspeople win'
    elif len(wolves)==len(all): winner='Werewolves win'
    c.log('\n%s'%winner,0,1,0)
    c.broadcast(winner,all)
    c.broadcast('close',all)
	

    c.log('End',1,1,1)
    if not test: os.chmod('log/%dm.log'%gameNumber,0744)
    if not test: os.system('echo "Game %d is over.  %s.  Please reconnect your client to play again." | wall'%(gameNumber,winner))
    exit()

if __name__=='__main__':
    main()
