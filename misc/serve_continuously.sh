#!/bin/bash
set -euox pipefail
IFS=$'\n\t'
ini=$1.ini

while :
do
    git pull
    pserve ${ini}
done


echo "" | mail -s "MCDP stopped" root@localhost
