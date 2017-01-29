#!/bin/bash
set -euox pipefail
IFS=$'\n\t'

i=${CIRCLE_NODE_INDEX}
db=out/comptests/compmake
outartifacts=$1
outreports=$2
outcompmake=${outartifacts}/compmake-stats

echo Output dir = ${outartifacts}
echo Output outcompmake = ${outcompmake}
mkdir -p ${outartifacts}
mkdir -p ${outcompmake}
bash -c "./misc/t 'config colorize 0; stats'   > ${outcompmake}/stats-${i}.txt"
bash -c "./misc/t 'config colorize 0; ls'       > ${outcompmake}/ls-${i}.txt"
bash -c "./misc/t 'config colorize 0; why failed'     > ${outcompmake}/why_failed-${i}.txt"
bash -c "./misc/t 'config colorize 0; stats failed'   > ${outcompmake}/stats_failed-${i}.txt"
bash -c "./misc/t 'config colorize 0; ls failed'       > ${outcompmake}/ls_failed-${i}.txt"
bash -c "./misc/t 'config colorize 0; details failed' > ${outcompmake}/details_failed-${i}.txt"
bash -c "./misc/t 'config' > ${outcompmake}/config-${i}.txt"

mkdir -p out/comptests-failures # in case there was no failure
cp -R out/comptests-failures ${outartifacts}/comptests-failures
#
mkdir -p ${outreports}
python src/mcdp_tests/comptest_to_junit.py ${db} > ${outreports}/junit.xml
cp ${outreports}/junit.xml ${outartifacts}/junit-${i}.xml
bash -c "pip freeze    > ${outartifacts}/pip_freeze_all-${i}.txt"
bash -c "pip freeze -l > ${outartifacts}/pip_freeze_local-${i}.txt"

echo End of $0

echo Artifacts:
find ${outartifacts}
echo Reports:
find ${outreports}
