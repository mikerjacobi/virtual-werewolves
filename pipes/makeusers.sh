echo 'setting up user: 'group$1
sudo adduser group$1 
sudo usermod -a -G group$1 moderator

mkfifo sto$1D/sto$1
chmod 420 sto$1D/sto$1
mkfifo $1tosD/$1tos
chmod 240 $1tosD/$1tos

chown group$1 sto$1D/sto$1
chown group$1 $1tosD/$1tos
chgrp group$1 sto$1D/sto$1
chgrp group$1 $1tosD/$1tos

chown group$1 sto$1D
chown group$1 $1tosD
chgrp group$1 sto$1D
chgrp group$1 $1tosD
