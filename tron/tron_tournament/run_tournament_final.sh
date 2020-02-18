#!/usr/local/bin/bash

set -e # exit on error

cd /course/cs1410/grading/TronTournamentFinal/

rm -rf ./submit-0/
rm -rf ./submit-0-autoreports/
mkdir submit-0
mkdir submit-0-autoreports

cp /course/cs1410/handin/TronTournament/* ./submit-0/
cd submit-0

for file in ./*
do
    full_name=$(basename $file)
    name=$(echo $full_name | cut -d"." -f1)
    mkdir $name
    tar --ignore-failed-read -xzf $full_name --strip-components 1 -C $name || echo "Failed $name"
    rm $full_name
done

chgrp -R cs-1410ta .
chmod -R 770 .
chgrp -R cs-1410ta ../submit-0-autoreports
chmod -R 770 ../submit-0-autoreports

echo "Files are in place, now run the tournament!"
echo "cd /course/cs1410/projects/tron/tron_tournament/"
echo "time python tournament.py TronTournamentFinal"
