# Description: This script will download bad IP addresses from different
# sources and block them using iptables and ipset
# author: Alexander Garzon

import os
import requests
import subprocess
import yaml
import ipaddress

# Check if ipset and iptables are installed
try:
    subprocess.check_output(['which', 'ipset'])
    subprocess.check_output(['which', 'iptables'])
except subprocess.CalledProcessError:
    print('Please install ipset and iptables before running the script')
    exit(1)

# Load configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

ipset_name = config['ipset_name']

# Check if ipset called badboys exists if not create it
try:
    subprocess.check_output(['ipset', 'list', ipset_name])
except subprocess.CalledProcessError:
    # Create ipset
    os.system(f'ipset create {ipset_name} hash:net maxelem 10000000')

# Download and merge bad IP addresses
bad_ips = set()
for url in config['badboys_urls']:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            for line in response.text.splitlines():
                # Remove comments
                if not line.startswith('#') and not line.startswith(';'):
                    ip = line.strip().split()[0]  # get only the IP
                    bad_ips.add(ip)
    except:
        pass

# Remove whitelisted IPs from bad_ips
for ip in config['whitelist_ips']:
    if '/' in ip:
        subnet = ipaddress.ip_network(ip, strict=False)
        for addr in subnet:
            bad_ips.discard(str(addr))
    else:
        bad_ips.discard(ip)

# clear ipset before adding
os.system(f'ipset flush {ipset_name}')

# Add bad IPs to ipset
for ip in bad_ips:
    if ip:
        os.system(f'ipset add {ipset_name} {ip}')
    else:
        print(f'Error adding {ip} to ipset')

# Delete previous iptables rule
os.system(f'iptables -D INPUT -m set --match-set {ipset_name} src -j DROP')

# Add new iptables rule
os.system(f'iptables -I INPUT -m set --match-set {ipset_name} src -j DROP')

# Display number of entries in ipset
print(subprocess.check_output(
    f"ipset list {ipset_name} | grep 'Number of entries' | cut -d' ' -f4", shell=True).decode('utf-8').strip())
