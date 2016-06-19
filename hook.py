#!/usr/bin/env python3

import argparse
import time

import dns.exception
import dns.resolver

def get_host_authoritative_nameservers(host):
    auth_nameservers = []
    soa_answer = dns.resolver.query(host, dns.rdatatype.SOA, raise_on_no_answer = False)
    soa_response = soa_answer.response
    rrset = None

    if soa_answer.rrset:
        soa_rrset = soa_response.answer[0]
    else:
        soa_rrset = soa_response.authority[0]

    # Parent host is the one with NS records, which may not be the same as host
    parent_host = soa_rrset.name

    ns_answer = dns.resolver.query(parent_host, dns.rdatatype.NS)

    for ns_rrset in ns_answer.rrset:
        auth_nameservers.append(ns_rrset.to_text())

    return auth_nameservers

def get_host_ip_addresses(host):
    ip_addresses = []
    ip_answer = dns.resolver.query(host, dns.rdatatype.A)

    for ip_rrset in ip_answer.rrset:
        ip_addresses.append(ip_rrset.to_text())

    return ip_addresses

def verify_challenge(host, challenge, ns_ip_addresses):
    nameserver_count = len(ns_ip_addresses)
    record_match_count = 0

    for ns_ip in ns_ip_addresses:
        # Use the authoritative server as a resolver - this works since we
        # will only issue queries where the resolver is
        print("+++ Check auth resolver with IP: " + ns_ip)
        auth_resolver = dns.resolver.Resolver(configure = False)
        auth_resolver.nameservers = [ns_ip]

        print("+++ Query for " + host + " TXT record")
        dns_answer = auth_resolver.query(host, 'TXT')

        if dns_answer:
            for dns_rrset in dns_answer.rrset:
                dns_text = dns_rrset.to_text()

                # DNS library quotes returned strings - for comparisons we
                # need to remove them
                if dns_text.startswith('"') and dns_text.endswith('"'):
                    dns_text = dns_text[1:-1]

                print("++++ Challenge: " + challenge)
                print("++++ DNS response: " + dns_text)

                if dns_text == challenge:
                    record_match_count += 1
                    break

    return (record_match_count == nameserver_count and record_match_count >= 1)

LOOKUP_SLEEP_SECONDS = 60
MAX_DNS_ATTEMPTS = 10
DEFAULT_TTL = 120

# Parse command line arguments
# Use nargs = '?' because not all arguments will be specified each time the
# hook script is called
parser = argparse.ArgumentParser()
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
    nameservers = get_host_authoritative_nameservers(domain)
    ns_ip_addresses = []

    for nameserver in nameservers:
        host_ip_addresses = get_host_ip_addresses(nameserver)
        for host_ip_address in host_ip_addresses:
            ns_ip_addresses.append(host_ip_address)

    print(ns_ip_addresses)

    for current_attempt in range(MAX_DNS_ATTEMPTS):
        print("++ Checking for DNS record, attempt: {}/{}".format(current_attempt+1, MAX_DNS_ATTEMPTS))

        try:
            if verify_challenge(host, challenge, ns_ip_addresses):
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
