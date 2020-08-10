while :; do
  echo -e "Send";
  ./leptgraypng >x.png; 
  #sshpass -p "0905  09" scp x.png tho@192.168.100.6:;
  #sshpass -p "0905  09" rsync -avz -e ssh x.png tho@192.168.100.6:receive;
done