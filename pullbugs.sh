#!/bin/bash
desclistfile="short_desc_list.txt"
versions=(24 25 26)
statuses=("CLOSED")

while read -r line
do
	DESC=$line
	# Loop through the version and bug status list
	for VER in "${versions[@]}"
	do
		for STAT in "${statuses[@]}"
		do
			python buggrabber.py -d "$DESC" -v $VER -s $STAT
		done
	done
done < "$desclistfile"
