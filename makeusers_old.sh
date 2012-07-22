echo 'making user: '$1
sudo useradd $1
sudo passwd $1
sudo usermod moderator -G $1
sudo mkfifo sto$1
sudo mkfifo $1tos
chown $1 sto$1
chown $1 $1tos
chgrp $1 sto$1
chgrp $1 $1tos
chmod 240 $1tos
chmod 420 sto$1
