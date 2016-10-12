import dns.exception
import dns.resolver

def get_host_authoritative_nameservers(host):
    auth_nameservers = []
    soa_answer = dns.resolver.query(host, dns.rdatatype.SOA, raise_on_no_answer = False)
    soa_response = soa_answer.response
    rrset = None

    # If we have an ANSWER, use that, otherwise use the AUTHORITY section (which
    # will be the nameservers for the parent host)
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

def verify_challenge(host, challenge, ns_ip_addresses, verbose = False):
    nameserver_count = len(ns_ip_addresses)
    record_match_count = 0

    # Check that every nameserver IP contains the challenge record
    for ns_ip in ns_ip_addresses:
        # Use the authoritative server as a resolver - this works since we
        # will only issue queries where the resolver is the authority (i.e.
        # recursive queries are not required)
        if verbose:
          print("+++ Check auth resolver with IP: " + ns_ip)

        auth_resolver = dns.resolver.Resolver(configure = False)
        auth_resolver.nameservers = [ns_ip]

        if verbose:
          print("+++ Query for " + host + " TXT record")

        dns_answer = auth_resolver.query(host, 'TXT')

        if dns_answer:
            for dns_rrset in dns_answer.rrset:
                dns_text = dns_rrset.to_text()

                # DNS library quotes returned strings - for comparisons we
                # need to remove them
                dns_text = dns_text.strip('"')

                if verbose:
                  print("++++ Challenge: " + challenge)
                  print("++++ DNS response: " + dns_text)

                if dns_text == challenge:
                    record_match_count += 1
                    break

    return (record_match_count == nameserver_count and record_match_count >= 1)
