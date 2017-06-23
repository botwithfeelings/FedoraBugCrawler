#!/bin/bash
desclistfile="short_desc_list.txt"
versions=(26)
statuses=("CLOSED")

LONGDESC=""
while read -r line
do
    if [ -z "$LONGDESC" ]; then
        LONGDESC+="$line"
    else
        LONGDESC+=", $line"
    fi
done < "$desclistfile"

# Loop through the version and bug status list
for VER in "${versions[@]}"
do
    for STAT in "${statuses[@]}"
    do
        python buggrabber.py -d "$LONGDESC" -v $VER -s $STAT
    done
done
