 #!/bin/bash
 if [[ $1 = "--start" ]] ; then
 	echo "Waiting for docker daemon to start up:"
    docker_file='Dockerfile'
    until docker ps 2>&1| grep STATUS>/dev/null; do  sleep 1; done;  >/dev/null
    docker ps -a | grep docker_graph
    if [ $? -eq 0 ]; then
            echo "Docker detected, Launching... "
            docker start docker_graph &
    elif [ -f $docker_file ]; then
            echo "Docker not found, Creating fandango-source-credibility Docker..."
            docker build -t image_neo4j . &
            wait
            docker run -t -p 5000:5000 -p 7474:7474 -p 7687:7687 --name docker_graph image_neo4j &                
    else
            echo "Docker & repository not found locally, Pulling it from Dockerhub "
            #TO DO
            #docker pull tavitto16/image_neo4j:latest
    fi
	echo "Docker started, activating stream service... (it lasts around 60 seconds)"
    sleep 20
            docker run -t -p 5000:5000 -p 7474:7474 -p 7687:7687 --name docker_graph image_neo4j &                
    else
        	echo "Docker & repository not found locally, Pulling it from Dockerhub "
            #TO DO
            docker pull tavitto16/image_neo4j:latest
    fi
	echo "Docker started, activating stream service... (it lasts around 60 seconds)"
    sleep 30
    wget --server-response --spider --quiet "http://0.0.0.0:5000/graph/stream/start" 2>&1 | awk 'NR==1{print $2}'
    if [ $? -eq 200 ]; then
            echo "Stream sevice not started"
    else
        	echo "fandango-source-credibility service ready..."
    fi
elif [[ $1 = "--stop" ]] ; then
        echo "stoping services..."
        wget --server-response --spider --quiet "http://0.0.0.0:5000/graph/stream/stop" 2>&1 | awk 'NR==1{print $2}'
        if [ $? -eq 200 ]; then
                echo "Stream sevice not stopped"
        else
            	echo "Preprocessing service stopped..."
        fi
	echo "stoping docker..."
        docker stop docker_graph
else
    	echo "Please add the correct option  [--start]  or [--stop]"
fi
fi
