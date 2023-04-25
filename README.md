# FLEX_KEEPER
A python script to help you mangae Fortinet FLEX licenses.  Great for lab work.


This is my new version of FLEX KEEPER.  It was pretty much a total re-write.  After witnessing a user use 
the script I undertood that my flow was just silly and didn't scale.  In this version I use a CSV file 
to store the VMS info and parse it as you go.  It is import to note that when the script is launced it creates 
that file.  Once you start changing things that file will get out of sync with real world.  There is an 
option to regenerate the file.

Pyhton script to manage and control Fortinet FLEX VMs

This script will interface with the Fortinet support site and let you manage by CLI your FLEX VMs.

It allows you to List all current ACTIVE, STOPPED and PENDING vms. It allows you to stop active VMs. It allows you to decomission stopped and pending vms.

You will need to create an IAM API user that has read/write to both the FLEX module and the asset management.

Download the credentials and put them in the YAML file provided.

Included in the file is the Python libary requirements...

pip3 install -r requirements.txt
