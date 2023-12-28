# Description: This script will download bad IP addresses from different
# sources and block them using iptables and ipset
# author: Alexander Garzon

import os
import requests
import subprocess
import yaml
import ipaddress

def is_installed(tool):
    try:
        subprocess.check_output(['which', tool], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        raise RuntimeError(f'{tool} is not installed.')

def load_config(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def create_ipset(name):
    try:
        subprocess.check_output(['ipset', 'list', name], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        subprocess.run(['ipset', 'create', name, 'hash:net', 'maxelem', '10000000'], check=True)

def get_bad_ips(urls):
    bad_ips = set()
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            for line in response.text.splitlines():
                if not line.startswith(('#', ';')):
                    ip = line.strip().split()[0]
                    if validate_ip(ip):
                        bad_ips.add(ip)
        except requests.RequestException:
            pass
    return bad_ips

def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def retrieve_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except requests.RequestException:
        print('Could not retrieve public IP address')
        return None

def update_ipset(name, ips):
    subprocess.run(['ipset', 'flush', name], check=True)
    for ip in ips:
        subprocess.run(['ipset', 'add', name, ip], check=True)

def update_iptables(name):
    try:
        subprocess.run(['iptables', '-D', 'INPUT', '-m', 'set', '--match-set', name, 'src', '-j', 'DROP'], check=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        pass
    subprocess.run(['iptables', '-I', 'INPUT', '-m', 'set', '--match-set', name, 'src', '-j', 'DROP'], check=True)

def main():
    """
    This function is the entry point of the program.
    It performs the following steps:
    1. Checks if 'ipset' and 'iptables' are installed.
    2. Loads the configuration from 'config.yaml'.
    3. Creates an IP set using the specified name from the configuration.
    4. Retrieves a list of bad IP addresses from the specified URLs.
    5. Retrieves the public IP address.
    6. Adds the public IP address to the whitelist if it is not already present.
    7. Filters out the IP addresses in the whitelist from the list of bad IP addresses.
    8. Updates the IP set with the filtered IP addresses.
    9. Updates the iptables rules using the IP set.
    10. Prints the number of entries in the IP set.

    If any exception occurs during the execution, it will be caught and an error message will be printed.
    """
    try:
        is_installed('ipset')
        is_installed('iptables')
        print('ipset and iptables are installed')

        config = load_config('config.yaml')
        print(f"Loaded configuration: {config}")

        create_ipset(config['ipset_name'])
        print(f"IP set '{config['ipset_name']}' created")

        print('Retrieving bad IP addresses...')
        bad_ips = get_bad_ips(config['badboys_urls'])

        public_ip = retrieve_public_ip()
        if public_ip and public_ip not in config['whitelist_ips']:
            config['whitelist_ips'].append(public_ip)
        print(f"Public IP address: {public_ip}")

        filtered_ips = [ip for ip in bad_ips if ip not in config['whitelist_ips']]
        print(f"Filtered {len(bad_ips) - len(filtered_ips)} whitelisted IPs")

        update_ipset(config['ipset_name'], filtered_ips)
        print(f"IP set '{config['ipset_name']}' updated")

        update_iptables(config['ipset_name'])
        print('iptables rules updated')

        print(subprocess.check_output(f"ipset list {config['ipset_name']} | grep 'Number of entries'", shell=True).decode('utf-8').strip())

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
