#!/bin/bash
set -euox pipefail
IFS=$'\n\t'

while :
do
    git pull
    pserve needs_authentication.ini
done


echo "" | mail -s "MCDP stopped" root@localhost
