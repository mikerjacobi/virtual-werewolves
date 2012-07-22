sudo adduser moderator
sudo cp -r ./* /home/moderator
sudo chmod 701 /home/moderator/pipes
sudo chown moderator /home/moderator/config/*
sudo chgrp moderator /home/moderator/config/*
sudo chown moderator /home/moderator/log/*
sudo chgrp moderator /home/moderator/log/*
sudo chown moderator /home/moderator/*
sudo chgrp moderator /home/moderator/*
