#must be run as root
#add the users you wish to delete here in the manner shown below
#WARNING! this cannot be undone.

#userdel <username>
#groupdel <username>
#rm -rf /home/<username>

userdel moderator
groupdel moderator
rm -rf /home/moderator

userdel group1
groupdel group1
rm -rf /home/group1

userdel group2
groupdel group2
rm -rf /home/group2

userdel group3
groupdel group3
rm -rf /home/group3

