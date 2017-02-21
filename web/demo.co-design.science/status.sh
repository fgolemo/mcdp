echo `date`
dir=`dirname $0`

out=${dir}/status.png
tmp=${dir}/status.tmp.png

wget -O${tmp} "https://api.browshot.com/api/v1/simple?key=OGJL7hwDXO47n2LOWRnBZHyaG2p&url=http%3A//status.co-design.science&size=page"

mv ${tmp} ${out}

echo `date` > ${dir}/status.timestamp.txt
