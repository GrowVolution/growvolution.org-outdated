#!/bin/bash
set -e

apt-get update
apt-get install -y openssh-server redis-server sudo git curl

useradd -ms /bin/bash admin
echo 'admin ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

mkdir -p /home/admin/.ssh
echo '# Dev Team Keys' > /home/admin/.ssh/authorized_keys
chown -R admin:admin /home/admin/.ssh
chmod 700 /home/admin/.ssh
chmod 600 /home/admin/.ssh/authorized_keys

mkdir -p /var/run/sshd
echo "
PubkeyAuthentication yes
AuthorizedKeysFile %h/.ssh/authorized_keys
AllowUsers admin
PasswordAuthentication no
KbdInteractiveAuthentication no
UsePAM yes
ClientAliveInterval 120
" >> /etc/ssh/sshd_config
