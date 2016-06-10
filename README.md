# letsencrypt.sh-djbdns

Hook script for letsencrypt.sh with djbdns.

## Dependencies

 * `dnspython`: Package `python3-dnspython` in Ubuntu.

## DNS TTL

As the hook scripts checks once a minute for the challenge, you must set a low
TTL for the TXT record.

## Credits

Thanks to David Jones (@drjtwit) for help refactoring the main loop of the
script to be more Pythonic.
