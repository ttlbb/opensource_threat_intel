#!/bin/bash


# kill all scrapyd process
#pids=`ps aux | grep scrapyd | awk '{print $2}'`
pids=`pgrep scrapyd`
for pid in $pids
do
	kill -9 $pid
done
 
# remove scrapyd log
folder="../scrapyd_log"

if [ -d "$folder" ]; then
	rm -rf $folder 
fi

mkdir $folder

cd $folder


nohup scrapyd >/dev/null 2>&1 &

#curl http://localhost:6800/delproject.json -d project=opensource_threat_intel
scrapyd-deploy -p opensource_threat_intel

echo 'deploy opensource_threat_intel project success.'

echo 'start perform schedule tasks...'

#you can use crontab execute task
# 0 */4 * * *  bash /../../opensource_threat_intel/tools/scrapyd_crontab_task.sh
../tools/scrapyd_crontab_task.sh




