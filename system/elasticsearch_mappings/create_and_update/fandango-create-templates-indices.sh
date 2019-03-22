#!/bin/bash

#Include our config file
MY_DIR=$(pwd)
setupConf=$(echo "$MY_DIR" | sed 's/ /\\ /g')
. $setupConf/setup.config

#URL construction components
delimeter=":"
slash="/"
template="/_template/"
declare -a templates=("fdg-article" "fdg-media" "fdg-claim" "fdg-claim-review" "fdg-fact" "fdg-entity" "fdg-ap-person" "fdg-ap-organization" "fdg-topic")

#Loop through index names to delete template and index if exists, then add template as defined in json file, then add index
for i in "${templates[@]}"
do
url="$hostBase$delimeter$portNumber$slash$i";
templateUrl="$hostBase$delimeter$portNumber$template$i";

templateFile="@$i.json"

curl -XDELETE $url &> log
curl -XDELETE $templateUrl &>log
curl -XPUT $templateUrl -H "Content-Type: application/json" -d $templateFile
curl -XPUT $url
done





