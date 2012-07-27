#Author: Mike Jacobi
#Test and Update: Xu Zhang
#Virtual Werewolf Game
#Instructors: Roya Ensafi, Jed Crandall
#Cybersecurity, Spring 2012

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

echo 'setting up user: 'group$1

#create a user and add it to the moderator group
sudo adduser group$1 
sudo usermod -a -G group$1 moderator

#create directory for user to server communication
sudo mkdir /home/moderator/pipes/$1'tosD'
sudo chown group$1 /home/moderator/pipes/$1'tosD'
sudo chgrp group$1 /home/moderator/pipes/$1'tosD'
sudo chmod 350 /home/moderator/pipes/$1'tosD'

#create directory for server to user communication
sudo mkdir /home/moderator/pipes/'sto'$1'D'
sudo chown group$1 /home/moderator/pipes/'sto'$1'D'
sudo chgrp group$1 /home/moderator/pipes/'sto'$1'D'
sudo chmod 530 /home/moderator/pipes/'sto'$1'D'

#create respective fifos
sudo mkfifo /home/moderator/pipes/sto$1D/sto$1
sudo chmod 530 /home/moderator/pipes/sto$1D/sto$1
sudo mkfifo /home/moderator/pipes/$1tosD/$1tos
sudo chmod 350 /home/moderator/pipes/$1tosD/$1tos

#setup fifo perms
sudo chown group$1 /home/moderator/pipes/sto$1D/sto$1
sudo chown group$1 /home/moderator/pipes/$1tosD/$1tos
sudo chgrp group$1 /home/moderator/pipes/sto$1D/sto$1
sudo chgrp group$1 /home/moderator/pipes/$1tosD/$1tos
sudo chown group$1 /home/moderator/pipes/sto$1D
sudo chown group$1 /home/moderator/pipes/$1tosD
sudo chgrp group$1 /home/moderator/pipes/sto$1D
sudo chgrp group$1 /home/moderator/pipes/$1tosD

#add files to the new user's home directory
sudo cp client.py /home/group$1
sudo chmod 700 /home/group$1/client.py
sudo chown group$1 /home/group$1/client.py
sudo chgrp group$1 /home/group$1/client.py
