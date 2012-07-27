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


sudo adduser moderator
sudo cp -r ./* /home/moderator
sudo mkdir /home/moderator/pipes
sudo chmod 701 /home/moderator/pipes
sudo chown moderator /home/moderator/config/*
sudo chgrp moderator /home/moderator/config/*
sudo chown moderator /home/moderator/log/*
sudo chgrp moderator /home/moderator/log/*
sudo chown moderator /home/moderator/*
sudo chgrp moderator /home/moderator/*
