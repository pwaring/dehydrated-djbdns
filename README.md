# letsencrypt.sh-djbdns

Hook script for [letsencrypt.sh](https://github.com/lukas2511/letsencrypt.sh)
with [djbdns](http://cr.yp.to/djbdns.html).

## Dependencies

 * Python 3.x. The hook script will not work in Python 2.x.
 * `dnspython`: Package `python3-dnspython` in Ubuntu.

## Usage

To use this script, run `letsencrypt.sh` as normal with the following additional
command line arguments:

 * `--hook /path/to/hook.py`
 * `--challenge dns-01`

Each time the script receives a DNS challenge, it will print the relevant
djbdns record to the screen and pause. You should add this record to your
servers in the normal way and then press enter. The hook script will then
query the nameservers for the domain until all of them respond with the correct
challenge, at which point it will hand control back to `letsencrypt.sh`. By
default, the hook script will query the nameservers once a minute and make 10
attempts before giving up.

This hook script intentionally has little in the way of error checking and
allows all exceptions to bubble up to the top level. When this happens, Python
should exit with a non-zero return code, which `letsencrypt.sh` will see as an
error and halt. It is then up to the user to fix the relevant issue (e.g. if
the domain name passed as a parameter to `letsencrypt.sh` does not exist).

## Credits

Thanks to David Jones (@drjtwit) for help refactoring the main loop of the
script to be more Pythonic.
