#!/bin/python3

# will clean all of this up with time

import subprocess
import math
import ipaddress
import sys
import socket
import argparse
import platform
import time

def ping_that_ip(ip):
    # B/C Windows and Linux use differnt flags for a number ping, we'll account for both
    flag = "/n" if platform.system().lower() == "windows" else "-c"
    command = ['ping', flag, '1', str(ip)]
    
    try:
        # Runs the command while also keep track of the times
        start = time.time()
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=3)
        end = time.time()

        # If the command was ran succesfully (exit 0) then it will continue on by giving out the time
        if output.returncode == 0:
            response_time = math.floor((end-start)*1000) # Returns the number of milliseconds, floored
            return "UP", response_time, None
        
        # Else wise it will return an error
        else:
            return "DOWN", None, output.stderr
    
    # If it was a timeout error the following will proceed (timeout=3 gives the command 3 seconds to execute before it will terminate)
    except subprocess.TimeoutExpired:
        return "ERROR", None, "REQUEST TIMED OUT."
    
def ping_that_port(ip, port):
    try:
        # Will attempt to reach the desired port
        with socket.create_connection((ip, port), timeout=3):
            # Will return the port if it was reached
            return port
    
    # Given a 3 second timeout (similar to above), or another connection error, it will return None
    except (socket.timeout, ConnectionRefusedError):
        return None

# LETS THROW IT ALL TOGETHER
def main():
    # Switch from sys to argparse for this part
    # flag = sys.argv[1]
    # port = sys.argv[2]
    # cidr = sys.argv[3]
    parser = argparse.ArgumentParser
    parser.add_argument("cidr")
    parser.add_argument("-p", "--ports")
    
    args = parser.parse_args()

    # This will basically just check that a valid IP Address and will return the respective network for the address
    try:
        netwrk = ipaddress.ip_network(parser.cidr, strict=True)
    
    # Should strict turn to False, it will return the ValueError and return the error message to the user
    except ValueError as e:
        print("Please provide a valid CIRD notation network range. Double check and try again.")
        sys.exit(1)

    # Just some messages for the user
    print(f"Scanning network {parser.cidr}...")
    print(f"Total number of found hosts: {netwrk.num_addresses - 2} (not including network and broadcast hosts)")

    # Basically make a list of the up hosts and then scan the ports under it
    # So if the host is up use ping_that_port and then output them all yk
    # Can use this (below) should -p not be passed

    # Begins to iterate through each ip found in the range
    for ip in netwrk.hosts():
        # ping_that_ip returns will return three values
        status, response_time, error = ping_that_ip(ip)

        # If the host is up it will return this
        if status == "UP":
            print(f"{ip}: {status} [Response Time: {response_time} ms]")
        
        # If the host is down it will return this instead
        else:
            print(f"{ip}: {status} [Error: {error}]")

    sys.exit(0)

if __name__=="__main__":
    main()