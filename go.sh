#!/bin/bash

. venv/bin/activate

export FLASK_APP=bpg2.py
export FLASK_DEBUG=1
export GNUPGHOME=$( pwd )/gnupg

#killall multichaind
#sleep 1
#rm -rf ~/.multichain

if [[ ! -f bpg2.db ]]
then
    sqlite3 bpg2.db < schema.sql
fi

if [[ ! -d uploaded ]]
then
    mkdir uploaded
fi

if [[ ! -d check ]]
then
    mkdir check
fi


# Check gpg key environment
if [[ ! -d gnupg ]]
then
    mkdir gnupg
    tar -xzvf gnupg.tgz
    chmod 700 gnupg
fi

if [[ ! -d signed ]]
then
    mkdir signed
fi



flask run --host=0.0.0.0
#python ./bpg2.py
