import subprocess
import os

Bash_script_location = os.path.join(os.getcwd(), "flirpi", "single_read.sh")
while True:
    # rc = subprocess.call("/home/tho/Lepton_Project/Test_folder/Test_bash.sh", shell=True)
    rc = subprocess.call(Bash_script_location, shell=True)
