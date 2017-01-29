#!/bin/bash
set -euox pipefail
dest=frankfurt.co-design.science
build_dir=from-circle/builds/${CIRCLE_BUILD_NUM}
# instance dir
# /dir=${build_dir}/${CIRCLE_NODE_INDEX}

mkdir -p ~/.ssh/
keyname=~/.ssh/circle@frankfurt
python -c "print ${circle_frankfurt_key}" > ${keyname}
chmod 600 ${keyname}
echo -e "Host ${dest}\n  IdentityFile ${keyname}\n" >> ~/.ssh/config
#cat ~/.ssh/config
#cat ${keyname}

SS="ssh circle@${dest}"

${SS} cat /etc/hostname
${SS} mkdir -p ${build_dir}


rsync -av ${CIRCLE_ARTIFACTS}/ circle@${dest}:${build_dir}/
${SS} chmod -R o+rX ${build_dir}

last_link=/home/circle/public_html/last-build
${SS} rm -f ${last_link}
${SS} ln -f -s /home/circle/${build_dir} ${last_link}


manual=src/mcdp_data/libraries/manual.mcdplib/out-versions
mkdir -p ${manual}
rsync -av ${manual}/  circle@${dest}:${build_dir}/manual-out-versions/
