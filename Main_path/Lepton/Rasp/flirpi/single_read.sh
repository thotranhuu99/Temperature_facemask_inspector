#!/bin/bash
# ~/Github/Lepton_Project/Lepton_PC/flirpi/leptgraypng >/mnt/ramdisk/temp.png;
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
${DIR}/leptgraypng >/mnt/ramdisk/temp.png
