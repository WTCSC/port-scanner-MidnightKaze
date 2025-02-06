#!/bin/python3

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
        # Runs the command while also keeping track of the times
        start = time.time()
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=3)
        end = time.time()

        # If the command was ran succesfully (exit 0) then it will continue on by giving out the time
        if output.returncode == 0:
            response_time = math.floor((end-start)*1000) # Returns the number of milliseconds, floored
            return "UP", response_time, None
        
        # Else it will return an error
        else:
            return "DOWN", None, output.stderr
    
    # If it was a timeout error the following will proceed (timeout=3 gives the command 3 seconds to execute before it will terminate)
    except subprocess.TimeoutExpired:
        return "ERROR", None, "REQUEST TIMED OUT."
    
def ping_that_port(ip, port):
    try:
        # Will attempt to reach the desired port
        with socket.create_connection((ip, port), timeout=1):
            # Will return the port if it was reached
            return port
    
    # Given a 1 second timeout (similar to above), or another connection error, it will return None
    except (socket.timeout, ConnectionRefusedError):
        return None
    
def parse_dem_ports(port_string):
    ports = set()
    try:
        # Splits the ports at a comma if a list of ports is given
        for port in port_string.split(","):
            
            # Like wise, if a range is given it will map the range instead
            if "-" in port:
                start, end = map(int, port.split("-"))
                ports.update(range(start, end + 1))

            # If it's just a single port it will add it to the set as is
            else:
                ports.add(int(port))
        
        return sorted(ports)

    # Should none of those occur it will ask the user to reformat the input
    except ValueError:
        raise argparse.ArgumentTypeError("Please provide a valid port format. Ex: -p 80, -p 80,120,127, -p 1-100")

# LETS THROW IT ALL TOGETHER
def main():

    # Uses argparse to handle passed arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("cidr")
    parser.add_argument("-p", "--ports")
    
    args = parser.parse_args()

    # This will basically just check that a valid IP Address and will return the respective network for the address
    try:
        netwrk = ipaddress.ip_network(args.cidr, strict=True)
    
    # Should strict turn to False, it will return the ValueError and return the error message to the user
    except ValueError as e:
        print("Please provide a valid CIRD notation network range. Double check and try again.")
        sys.exit(1)

    # Just some messages for the user
    print(f"Scanning network {args.cidr}...")
    print(f"Total number of found hosts: {netwrk.num_addresses - 2} (not including network and broadcast hosts)")

    up_hosts= []

    # Begins to iterate through each ip found in the range
    for ip in netwrk.hosts():
        # ping_that_ip returns will return three values
        status, response_time, error = ping_that_ip(ip)

        # If the host is up it will return this
        if status == "UP":
            up_hosts.append(str(ip))
            print(f"[+] {ip}: {status} [Response Time: {response_time} ms]")
        
        # If the host is down it will return this instead
        else:
            print(f"[-] {ip}: {status} [Error: {error}]")

    # If ports were given, then it will look for those ports on up hosts.
    if args.ports and up_hosts:
        print ("\nScanning open ports on online (UP) hosts...")
        ports = parse_dem_ports(args.ports)
        # For each ip of an up host, it will "ping" the port(s)
        for ip in up_hosts:
            for port in ports:
                if ping_that_port(ip, port):
                    # Will only print this if the port is actually open
                    print (f"[OPEN] {ip}: {port}")

    sys.exit(0)

if __name__=="__main__":
    main()

# Change the format so that the ports follow the up hosts or something like that
# Test this (below) later

"""
if status == "UP":
    print(f"[+] {ip}: {status} [Response Time: {response_time} ms]")
    ports = parse_dem_ports(args.ports)
    for port in ports:
        if ping_that_port(ip, port):
        print (f"[OPEN]: {port}")
"""