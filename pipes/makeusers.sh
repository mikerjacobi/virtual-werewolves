echo 'setting up user: 'group$1

#create a user and add it to the moderator group
sudo adduser group$1 
sudo usermod -a -G group$1 moderator

#create directory for user to server communication
mkdir $1'tosD'
chown group$1 $1'tosD'
chgrp group$1 $1'tosD'
chmod 240 $1'tosD'

#create directory for server to user communication
mkdir 'sto'$1'D'
chown group$1 'sto'$1'D'
chgrp group$1 'sto'$1'D'
chmod 420 'sto'$1'D'

#create respective fifos
mkfifo sto$1D/sto$1
chmod 420 sto$1D/sto$1
mkfifo $1tosD/$1tos
chmod 240 $1tosD/$1tos

#setup fifo perms
chown group$1 sto$1D/sto$1
chown group$1 $1tosD/$1tos
chgrp group$1 sto$1D/sto$1
chgrp group$1 $1tosD/$1tos
chown group$1 sto$1D
chown group$1 $1tosD
chgrp group$1 sto$1D
chgrp group$1 $1tosD
