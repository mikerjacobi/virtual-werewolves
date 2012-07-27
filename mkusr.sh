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
