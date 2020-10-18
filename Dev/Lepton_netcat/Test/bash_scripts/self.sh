#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd)" 
SCRIPT_LOC="${DIR}/hello.sh"
#printf "${SCRIPT_LOC}"
${SCRIPT_LOC}

