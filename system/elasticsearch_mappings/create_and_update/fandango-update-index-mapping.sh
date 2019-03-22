#!/bin/bash

#Include our config file
MY_DIR=$(pwd)
setupConf=$(echo "$MY_DIR" | sed 's/ /\\ /g')
. $setupConf/setup.config

#URL construction components
delimeter=":"
slash="/"
mappings="/_mapping/_doc"
declare -a templateUpdates=("fdg-article" "fdg-media" "fdg-claim" "fdg-claim-review" "fdg-fact" "fdg-entity" "fdg-ap-person" "fdg-ap-organization" "fdg-topic")

#Loop through index names to  add new mappings as defined in idnex' corresponding update json file
for i in "${templateUpdates[@]}"
do
url="$hostBase$delimeter$portNumber$slash$i$mappings";
echo $url

templateFile="@update-$i.json"

curl -XPUT $url -H "Content-Type: application/json" -d $templateFile
done