import os
import sys

numUsers=int(sys.argv[1])
for i in range(numUsers):
	os.system("./mkusr.sh "+str(i+1))
