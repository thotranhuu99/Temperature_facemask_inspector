#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd)"
Single_read_loc="${DIR}/leptgraypng"
SCRIPT="${Single_read_loc} > /mnt/ramdisk/temp.png"
#printf "${SCRIPT_LOC}"
${SCRIPT}