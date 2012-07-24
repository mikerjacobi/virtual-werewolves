#must be run as root
userdel moderator
userdel group1
userdel group2
userdel group3
groupdel moderator
groupdel group1
groupdel group2
groupdel group3

rm -rf /home/moderator
rm -rf /home/group*
