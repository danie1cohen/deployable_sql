#!/bin/bash
export TZ=America/Los_Angeles
export DEBIAN_FRONTEND=noninteractive

apt-get -qq update
apt-get -qqy install build-essential libssl-dev libffi-dev python3-dev python3-pip
apt-get -qqy --no-install-recommends install git-core

pip3 install -q --upgrade pip
pip3 install -q pyopenssl ndg-httpsclient pyasn1

# set up virtual envs
pip3 install -q virtualenvwrapper

if [ -d "/vagrant" ]; then
    echo "Setting home user to: vagrant"
    HOME_USER=vagrant
    # set python3 as primary python
    ln -sfn `which python3` `which python`
else
    echo "Setting home user to: `SUDO_USER`"
    HOME_USER=`SUDO_USER`
fi

# set up virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=/opt/envs/

# set up a useful bash profile
echo "# display last command and log it to bootstrap file
alias strap=\"history | tail -n2 | sed -n '1p'  | sed 's/^[0-9 ]*//' | sed 's/sudo //' >> /vagrant/bootstrap.sh && tail /vagrant/bootstrap.sh\"

# pip install and update requirements.txt
pipit() { pip install \"$1\" && pip freeze > /vagrant/requirements.txt; }

# set up virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=/opt/envs/

# always cd to shared folder first
cd /vagrant
workon arcu_sql" >> /home/$HOME_USER/.bash_profile

if [ ! -d "/opt/envs" ]; then
    mkdir /opt/envs
fi
mkvirtualenv arcu_sql

if [ -a "/vagrant" ]; then
    cd /vagrant
    pip3 install -qr requirements.txt
fi

chown -R $HOME_USER:$HOME_USER /opt /home/$HOME_USER/.bash_profile

apt-get install -y freetds-dev > /dev/null # pymssql
