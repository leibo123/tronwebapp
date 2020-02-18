#!/usr/local/bin/bash

set -e # exit on error

cd /course/cs1410/grading/TronTournament/

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

cd /course/cs1410/projects/tron/tron_tournament/
source /course/cs1410/venv/bin/activate
time python /course/cs1410/projects/tron/tron_tournament/tournament.py

shopt -s nullglob # expand unmatched globs into empty list
python /course/cs1410/auto_grader/emailer.py --no-confirm TronTournament /course/cs1410/projects/tron/tron_tournament/error_message.txt /course/cs1410/grading/TronTournament/submit-0-autoreports/*
