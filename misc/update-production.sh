#!/bin/bash
set -euox pipefail
IFS=$'\n\t'


if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

inst=$1

branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')
echo Restart remote: ${inst}
echo Current branch: ${branch}

echo Merging
git branch -f ${inst} ${branch}
echo Push
git push --all
echo Restart production
wget -q -O- --content-on-error http://demo.co-design.science/${inst}/exit
