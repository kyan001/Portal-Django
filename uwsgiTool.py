#!/usr/bin/python3
# HISTORY
# -----------------------------------------------------------------
#     DATE    |     AUTHOR     |  VERSION | COMMENT
# ------------+----------------+----------+-----------------------
#  2015-01-13 |     YAN Kai    |   V1.0   | Script Creation
#  2015-04-05 |     YAN Kai    |   V1.1   | detect running
#  2015-08-07 |     YAN Kai    |   V1.2   | Merge
#  2016-07-07 |     YAN Kai    |   V1.3   | fix bug
# -----------------------------------------------------------------
import os
import sys
sys.path.append('/home/kyan001/KyanToolKit_Unix')

import KyanToolKit_Py
ktk = KyanToolKit_Py.KyanToolKit_Py()

# -Pre-conditions Check-------------------------------------------
ktk.needPlatform("linux")

# -set params-----------------------------------------------------
# config file
uwsgi_xml = "./uwsgi.xml"
if os.path.isfile(uwsgi_xml):
    ktk.info("uwsgi config file: " + uwsgi_xml)
else:
    ktk.err("uwsgi config file not found: " + uwsgi_xml)
# pid file
pid_file = "/var/run/uwsgi_portal_django.pid"
if os.path.exists(pid_file):
    ktk.warn("uwsgi is running @ " + pid_file)
else:
    ktk.info("No uwsgi running")
# choice
operations = ["start", "stop", "reload"]
oprtn = ""
if len(sys.argv) != 2:
    oprtn = ktk.getChoice(operations)
elif sys.argv[1] in operations:
    oprtn = sys.argv[1]
else:
    ktk.err("Wrong Params: " + sys.argv[1])
    ktk.byeBye()

# -run commands---------------------------------------------------
if "start" == oprtn:
    ktk.runCmd("sudo echo ''")
    ktk.runCmd("sudo uwsgi -x '" + uwsgi_xml + "' --pidfile '" + pid_file + "' &")
elif "stop" == oprtn:
    ktk.runCmd("sudo uwsgi --stop " + pid_file)
elif "reload" == oprtn:
    ktk.runCmd("sudo uwsgi --reload " + pid_file)
else:
    ktk.err("Wrong operation: " + oprtn)
    ktk.byeBye()
