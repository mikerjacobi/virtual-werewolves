echo 'updating '$1
sudo cp client.py /home/group$1/client.py
sudo chown group$1 /home/group$1/client.py
sudo chgrp group$1 /home/group$1/client.py
sudo chmod 740 /home/group$1/client.py
sudo rm /home/$1/.client.py.swp
