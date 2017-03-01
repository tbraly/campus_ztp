#!/usr/bin/python
 
import sys, os, time, json

# This script is called from st2_dhcp_webhook bash script

# Edit array of Vendor UIO to allow and how much time should elapse between
# duplicate requests from the same MAC address

valid_ouis = ['cc:4e:24','60:9c:9f']
max_timespan = 10  # In Seconds
tmp_dir = '/tmp'
 
if len(sys.argv) != 2:
    sys.stderr.write("Usage: %s DHCP_COMMIT_JSON_DATA\n" % sys.argv[0])
    exit(1)
try:
    vars = json.loads(sys.argv[1])
except Exception as e:
    sys.stderr.write("Could not process JSON input: %s\n" % e)
    exit(1)
 
if not 'client_mac' in vars:
    sys.stderr.write("Error, 'client_id' not found in JSON input\n")
    exit(1)
 
client_mac = vars['client_mac']
 
for oui in valid_ouis:
    if (client_mac.startswith(oui)):
        # This is a valid mac for ZTP, now see if it's a duplicate request in X seconds
 
        # See if there is a tmp mac file... if so load time
        mac_file_name = "%s/%s" % (tmp_dir,client_mac)
        if not os.path.isfile(mac_file_name):
            # No history, we're good, but record the time it worked!
            macfile = open(mac_file_name,'w')
            macfile.write("%d" % time.time())
            macfile.close()
            exit(0)
        else:
            curtime = time.time()
            macfile = open(mac_file_name,'r')
            lasttime = int(macfile.readline())
            macfile.close()
 
            diff = curtime - lasttime
            if diff < max_timespan:
                sys.stderr.write("This is a duplicate request within the %d seconds\n" % max_timespan)
                exit(1)
 
            macfile = open(mac_file_name,'w')
            macfile.write("%d" % time.time())
            macfile.close()
            print("Success!")
            exit(0)
 
        sys.stderr.write("Opps! Something when wrong!!!\n")
        exit(1)
 
sys.stderr.write("%s is not a valid allowed mac address.\n" % client_mac)
exit(1)
 
