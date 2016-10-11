#!/usr/bin/env python3
# usage:
#    ./uwsgiTool.py
#    python3 uwsgiTool.py
#    ./uwsgiTool.py start/stop/reload

import os
import sys

import consoleiotools as cit
import KyanToolKit
ktk = KyanToolKit.KyanToolKit()

# -Pre-conditions Check-------------------------------------------
ktk.needPlatform("linux")

# -set params-----------------------------------------------------
# config file
uwsgi_xml = "./uwsgi.xml"
if os.path.isfile(uwsgi_xml):
    cit.info("uwsgi config file: " + uwsgi_xml)
else:
    cit.err("uwsgi config file not found: " + uwsgi_xml)
# pid file
dir_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
pid_file = "/var/run/uwsgi_{}.pid".format(dir_name)
if os.path.exists(pid_file):
    cit.warn("uwsgi is running @ " + pid_file)
else:
    cit.info("No uwsgi running")
# choice
operations = ["start", "stop", "reload"]
oprtn = ""
if len(sys.argv) != 2:
    oprtn = cit.get_choice(operations)
elif sys.argv[1] in operations:
    oprtn = sys.argv[1]
else:
    cit.err("Wrong Params: " + sys.argv[1])
    cit.bye()

# -run commands---------------------------------------------------
if "start" == oprtn:
    ktk.runCmd("sudo echo ''")
    ktk.runCmd("sudo uwsgi -x '" + uwsgi_xml + "' --pidfile '" + pid_file + "' &")
elif "stop" == oprtn:
    ktk.runCmd("sudo uwsgi --stop " + pid_file)
elif "reload" == oprtn:
    ktk.runCmd("sudo uwsgi --reload " + pid_file)
else:
    cit.err("Wrong operation: " + oprtn)
    cit.bye()
