#mkdir $1'tosD'
chown $1 $1'tosD'
chgrp $1 $1'tosD'
chmod 240 $1'tosD'
mkdir 'sto'$1'D'
chown $1 'sto'$1'D'
chgrp $1 'sto'$1'D'
chmod 420 'sto'$1'D'
mv $1'tos' $1'tosD'
mv 'sto'$1 'sto'$1'D'
