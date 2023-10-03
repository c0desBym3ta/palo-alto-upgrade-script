#!/usr/bin/env python

"""
upgrade.py
==========

This script upgrades a Palo Alto Networks firewall or Panorama to the
specified version. It takes care of all intermediate upgrades and reboots.

For example. If the firewall is to 10.0.0 and you want to upgrade to 10.2.3, the script will install
10.1.0 and reboot, then 10.2.0 and reboot and finally 10.2.3 and reboot.
"""

"""Author"""
__author__ = "c0desbym3ta"

"""Importing system libraries and modulea"""
import sys
import os
import argparse
import logging
import requests
import os
import time

"""Importing palo alto libraries"""
from panos.base import PanDevice
from pan.xapi import PanXapiError

"""Importing other usefull libraries"""
from datetime import datetime
from threading import Timer
from getpass import getpass
from colorama import Fore

"""Getting palo alto absolute path. Necessary for the palo alto libraries."""
curpath = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(curpath, os.pardir)]

def upgrade(firewall_hostname, firewall_firmware, username, password):
    print(Fore.GREEN + "[+] Executed at ", datetime.now())
    # Get command line arguments
    parser = argparse.ArgumentParser(
        description="Upgrade a Palo Alto Networks Firewall or Panorama to the specified version"
    )
    parser.add_argument(
        "-v", "--verbose", action="count", help="Verbose (-vv for extra verbose)"
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="No output")
    parser.add_argument(
        "-n",
        "--dryrun",
        action="store_true",
        help="Print what would happen, but don't perform upgrades",
    )
    # Palo Alto Networks related arguments

    fw_group = parser.add_argument_group("Palo Alto Networks Device")

    ##fw_group.add_argument("hostname", help="Hostname of Firewall or Panorama")

    ##fw_group.add_argument("version", help="Target version")

    args = parser.parse_args()

    ### Set up logger
    # Logging Levels
    # WARNING is 30
    # INFO is 20
    # DEBUG is 10
    if args.verbose is None:
        args.verbose = 0
    if not args.quiet:
        logging_level = 20 - (args.verbose * 10)
        if logging_level <= logging.DEBUG:
            logging_format = "%(levelname)s:%(name)s:%(message)s"
        else:
            logging_format = "%(message)s"
        logging.basicConfig(format=logging_format, level=logging_level)

    # Connect to the device and determine its type (Firewall or Panorama).
    # This is important to know what version to upgrade to next.

    try:

        print(Fore.YELLOW + "[\] Connecting to ", firewall_hostname)
        device = PanDevice.create_from_device(firewall_hostname, username, password)
        print(Fore.GREEN + "[+] Connection established to ", firewall_hostname)

        # Perform the upgrades in sequence with reboots between each upgrade
        print(Fore.GREEN + f"[+] Upgrading {firewall_hostname}" + Fore.RESET)
        print(Fore.YELLOW)
        device.software.upgrade_to_version(firewall_firmware, args.dryrun)
        print (Fore.GREEN + "[+] Installed software version verified: ", device.refresh_system_info().version)
        print(Fore.WHITE + "############################################")
    except KeyboardInterrupt:
        print(Fore.RED + "[-] Exception thrown due to user keyboard interrupt")
        print(Fore.WHITE)
    except Exception as e:
        if "Invalid Credential" in str(e):
            print(Fore.RED + "[-] Invalid credentials. Please try again and insert correct credentials!")
            print(Fore.WHITE)
        else:
            print(Fore.RED + "[-] Some exception occured. Please check the following logs: ", str(e))
            print(Fore.WHITE)

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    elif os.name == 'posix':
        _ = os.system('clear')

def controll_arguments():
    if len(sys.argv) == 2: # If we have given two arguments
        print()##target = socket.gethostbyname(sys.argv[1]) # Define our target as argument 1
    else:
        print("Invalid amount of arguments!")
        print("Correct syntax: python3 pa-upgrade.py <ip> <firmware version>")


if __name__ == "__main__":
    clear()

    if len(sys.argv) == 1: # If we have given two arguments
        print("WELCOME TO PALO ALTO FIREWALL UPGRADE SCRIPT")
        print("############################################")
        print("1 - for executing the script now\n2 - to program execution")
        executionChoice = int(input("Enter your choice: "))
        if executionChoice == 1:
            clear()

            firewall_hostname = str(input(Fore.YELLOW + "Insert firewall hostname: "))
            firewall_firmware = str(input(Fore.YELLOW + "Insert firewall firmware version: "))
            username = str(input(Fore.YELLOW + "[\] Username: "))
            password = getpass("[\] Password: ")
            upgrade(firewall_hostname, firewall_firmware, username, password)
        elif executionChoice == 2:
            x = datetime.today()
            givenDate = int(input("Which day: (1 for tomorrow...): "))
            print("Give hours and minutes below ")
            givenHour = int(input("Hours: "))
            givenMinute = int(input("Minutes: "))

            print("Selected date and time: ", givenDate, " at " + str(givenHour) + ":" + str(givenMinute))
            y = x.replace(day=x.day + givenDate, hour=givenHour, minute=givenMinute, second=0, microsecond=0)
            delta_t = y - x

            clear()
            firewall_hostname = str(input(Fore.YELLOW + "Insert firewall hostname: "))
            firewall_firmware = str(input(Fore.YELLOW + "Insert firewall firmware version: "))
            username = str(input(Fore.YELLOW + "[\] Username: "))
            password = getpass("[\] Password: ")

            secs = delta_t.seconds + 1

            t = Timer(secs, upgrade, args=(firewall_hostname, firewall_firmware, username, password))
            t.start()
        else:
            print("Invalid choide :). Try again")
            time.sleep(3)
            clear()
    else:
        print(Fore.RED + "Invalid amount of arguments!")
        print(Fore.YELLOW + "Correct syntax: python3 pa_upgrade.py <ip> <firmware version>")
        print(Fore.WHITE)
        sys.exit()
