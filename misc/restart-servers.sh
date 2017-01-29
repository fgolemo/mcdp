#!/bin/bash
set -euox pipefail
IFS=$'\n\t'
#set -x

# branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

# echo Branch: ${branch}

echo
echo "Restarting local server"
echo
wget -O- --content-on-error http://127.0.0.1:8080/exit 2>/dev/null || (echo '\nFAILURE!'; exit 129)

#echo $?

# if [ ${branch} = "inst00" ]; then
#     echo "Restarting remote server"
#     wget -q -O- --content-on-error http://demo.co-design.science/inst00/exit
# fi
#echo $?
