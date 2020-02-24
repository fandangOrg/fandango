#!/bin/bash
echo "Launching server..."
python /app/init_services.py 
sleep 1m 
echo "Docker started, activating stream service... (it lasts around 60 seconds)"
wget --server-response --spider --quiet "http://0.0.0.0:5001/preprocess/stream/start" 2>&1 | awk 'NR==1{print $2}'
if [ $? -eq 200 ]; then
	echo "Stream sevice not started"
else
	echo "Preprocessing service ready..."	
fi
