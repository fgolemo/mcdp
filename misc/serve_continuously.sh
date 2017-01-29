#!/bin/bash
set -euox pipefail
IFS=$'\n\t'

while :
do
    git pull
    mcdp-web --delete_cache
done


echo "" | mail -s "MCDP stopped" root@localhost
