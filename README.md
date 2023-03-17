# Badboys - A simple python script to block bad IP addresses

<p align="center">
  <img alt="badboys" title="badboys" src="https://user-images.githubusercontent.com/339828/225473301-c80d16a2-7df7-408e-90eb-8888aef9e25c.svg" width="450">
</p>

A very simple python script to get bad IP addresses from a different URL and block them with iptable using ipset.

This script downloads bad IP addresses from different sources, removes whitelisted IPs from the list (supports subnet range CIDR), and then adds the remaining bad IPs to an ipset using the ipset command. It also flushes the existing ipset before adding the new bad IPs to it.

This script was inspired by: https://github.com/trick77/ipset-blacklist which I used for many many years.

But I felt that I want to redo it from scratch and make it more simple and easy to use but with Python.

It worth mentioning that this script was made possible thanks to chatGPT. Even though I do not code in Python, I was able to make this script thanks to chatGPT in no more than 2 hours. Even the logo was made by chatGPT 😮!

The Dockerfile was used for me only during the development phase and it is not needed for the script to work.

## Requirements

    - Python 3
    - ipset
    - iptables

# Usage

Create your own config.yaml file based on sample.config.yaml and then run the script with:

`python3 badboys.py`

# DEBUG

I use this code to see how many entryes are in the ipset

`ipset list badboys | grep 'Number of entries' | cut -d' ' -f4`

## Licence

MIT License
