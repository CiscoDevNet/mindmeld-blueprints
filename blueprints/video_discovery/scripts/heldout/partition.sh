#!/usr/bin/env bash

shuffle () {
		for filename in train*.txt; do
			while read line; do
				echo $filename$'\t'$line >> temp.txt
			done <$filename
		done
		gsort -R temp.txt > rand.txt
		rm temp.txt
}

partition() {
	head -n 300 rand.txt > tmp_heldout.txt
	tail -n 2932 rand.txt > tmp_training.txt
}

training() {
	while read line; do
		IFS=$'\t' read -r file query <<< "$line"
		echo $query >> $'new_'$file
	done <'tmp_training.txt'
}

heldout() {
    while read line; do
        IFS=$'\t' read -r _ query <<< "$line"
        echo $query >> heldout.txt
    done <'tmp_heldout.txt'
}

training
heldout
