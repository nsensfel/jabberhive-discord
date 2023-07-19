#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

while true
do
   $SCRIPT_DIR/jh-discord.py -t $2 -d $1 -c
   sleep 60
done
