#!/bin/bash

cd /home/anton.kronseder/dc-app-performance-toolkit-enterprise
source /home/anton.kronseder/dc-app-performance-toolkit-enterprise/venv/bin/activate
cd app

retval=$(bzt -q confluence.yml)
if [ $? -eq 0 ]; then
	retval2=$(python convert-to-projectdoc-json.py 235340405)
fi

echo "Commands returned $retval $retval2" | mail -s "Script Results $retval $retval2" anton.kronseder@smartics.de 
