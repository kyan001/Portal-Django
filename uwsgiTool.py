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

__version__ = '1.1.1'


def main():
    # precheck
    ktk.needPlatform("linux")
    # defines
    uwsgi_xml = "./uwsgi.xml"  # uwsgi config file
    pid_file = get_pid_file()  # exist when running
    # run
    check_config_file(uwsgi_xml)
    check_pid_file(pid_file)
    operation = get_operation()
    run_operation(operation, uwsgi_xml, pid_file)


def get_pid_file():
    """generate pid_file path and name according to script's dirname

    returns:
        '/var/run/uwsgi_dirname.pid'
    """
    dir_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    return "/var/run/uwsgi_{}.pid".format(dir_name)


def check_config_file(xml_file):
    """check if uswgi config file exists"""
    if os.path.isfile(xml_file):
        cit.info("uwsgi config file: " + xml_file)
    else:
        cit.err("uwsgi config file not found: " + xml_file)


def check_pid_file(pid_file):
    """check if this uwsgi is already running"""
    if os.path.exists(pid_file):
        cit.warn("uwsgi is running @ " + pid_file)
    else:
        cit.info("No uwsgi running")
    return pid_file


def get_operation():
    """start a new uwsgi, stop a running uwsgi, or reload the config and codes"""
    operations = ["start", "stop", "reload"]
    if len(sys.argv) != 2:
        return cit.get_choice(operations)
    elif sys.argv[1] in operations:
        return sys.argv[1]
    else:
        cit.err("Wrong Params: " + sys.argv[1])
        cit.bye()


def run_operation(oprtn, config_file, pid_file):
    if "start" == oprtn:
        ktk.runCmd("sudo echo ''")
        ktk.runCmd("sudo uwsgi -x '" + config_file + "' --pidfile '" + pid_file)
    elif "stop" == oprtn:
        ktk.runCmd("sudo uwsgi --stop " + pid_file)
    elif "reload" == oprtn:
        ktk.runCmd("sudo uwsgi --reload " + pid_file)
    else:
        cit.err("Wrong operation: " + oprtn)
        cit.bye()


if __name__ == '__main__':
    main()
