#!/bin/sh
while true; do
	tail -f -n0 -s 0.01 $1 | ./parse_lives.py
    echo "Script has crashed. It will restart immediately..., press CTRL-C to cancel"
done
