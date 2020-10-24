echo 'Transferring to 192.168.31.'$1
raspivid -vf -n -w 1200 -h 900 -fps 24 -o - -t 0 -b 2000000 | nc -u '192.168.31.'$1 5001
