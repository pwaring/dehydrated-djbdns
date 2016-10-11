#!/usr/bin/env python3

import argparse
import time

import dnsutil
import dns.exception
import dns.resolver

LOOKUP_SLEEP_SECONDS = 60
MAX_DNS_ATTEMPTS = 10
DEFAULT_TTL = 120

# Parse command line arguments
# Use nargs = '?' because not all arguments will be specified each time the
# hook script is called
parser = argparse.ArgumentParser(prefix_chars='@')
parser.add_argument("action", nargs = '?', default = '')
parser.add_argument("domain", nargs = '?', default = '')
parser.add_argument("token", nargs = '?', default = '')
parser.add_argument("challenge", nargs = '?', default = '')
# Extra positional argument to absorb any beyond the first four (we only
# care about four arguments because we only take action for deploy_challenge)
parser.add_argument("extra", nargs = '*', default = '')
args = parser.parse_args()

action = args.action
domain = args.domain
token = args.token
challenge = args.challenge

if action == 'deploy_challenge':
    print("++ Setting DNS for " + domain + " to " + challenge)
    host = "_acme-challenge." + domain
    record = "'" + host + ":" + challenge + ":" + str(DEFAULT_TTL)
    print("++ Copy the following line into your DNS zone for " + domain + " and upload")
    print(record)
    input("++ Press enter once DNS zone has been uploaded...")

    # Get the NS records for the domain, not the host, as the host record may
    # not exist yet
    print("++ Get NS IP addresses to query auth servers for " + domain)
    nameservers = dnsutil.get_host_authoritative_nameservers(domain)
    ns_ip_addresses = []

    for nameserver in nameservers:
        host_ip_addresses = dnsutil.get_host_ip_addresses(nameserver)
        for host_ip_address in host_ip_addresses:
            ns_ip_addresses.append(host_ip_address)

    print(ns_ip_addresses)

    for current_attempt in range(MAX_DNS_ATTEMPTS):
        print("++ Checking for DNS record, attempt: {}/{}".format(current_attempt+1, MAX_DNS_ATTEMPTS))

        try:
            if dnsutil.verify_challenge(host, challenge, ns_ip_addresses):
                print("++ Challenge successful!")
                break
        except dns.exception.Timeout:
            print("++ DNS timeout, quitting...")
            sys.exit(1)
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            pass

        time.sleep(LOOKUP_SLEEP_SECONDS)
    else:
        print("++ Failed to find record for: " + domain)
        sys.exit(1)
