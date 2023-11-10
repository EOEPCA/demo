#!/bin/bash
 
read -p "Client Id: " client_id

read -p "Client Name: " client_name

read -p "Client Description: " client_description

read -p "Add resource? y/n" add_resource

resources=()

while [ "$add_resource" == y ];
do 
    read -p "Resource name: " resource_name
 
    read -p "Resource URI: " resource_uri
 
    read -p "Users: " users

    resource="{"resource":{"name": "${resource_name}","uris": ["${resource_uri}"],"resource_scopes": ["access"]},"permissions": {"user":["${users}"]}}" 

    resources+=$resource

    read -p "Add resource? y/n" add_resource

done
payload="{"clientId": "${client_id}","name": "${client_name}","description":"${client_description}","resources": "$resources"}"

echo $payload