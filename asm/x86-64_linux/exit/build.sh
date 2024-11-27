#!/bin/sh
if [ -z "$1" ]
then
	echo "Building.."
	# Build object file
	as exit.s -o exit.o
	# Link executable
	ld exit.o -o exit
	# Run test
	./exit
	echo $?
elif [ "$1" == "-c" ] || [ "$1" == "--clean" ]
then
	echo "Cleaning.."
	rm exit.o
	rm exit
fi
