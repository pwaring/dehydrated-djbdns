# dehydrated-djbdns

Hook script for using [dehydrated](https://github.com/lukas2511/dehydrated)
to generate [djbdns](http://cr.yp.to/djbdns.html) records which can be used to
respond to DNS challenges for LetsEncrypt certificate issuance.

## Dependencies

 * Python 3.x. The hook script will not work in Python 2.x.
 * `dnspython`: Package `python3-dnspython` in Ubuntu.

## Usage

To use this script, run `dehydrated` as normal with the following additional
command line arguments:

 * `--hook /path/to/hook.py`
 * `--challenge dns-01`

Each time the script receives a DNS challenge, it will print the relevant
djbdns record to the screen and pause. You should add this record to your
servers in the normal way and then press enter. The hook script will then
query the nameservers for the domain until all of them respond with the correct
challenge, at which point it will hand control back to `dehydrated`. By
default, the hook script will query the nameservers once a minute and make 10
attempts before giving up.

This hook script intentionally has little in the way of error checking and
allows all exceptions to bubble up to the top level. When this happens, Python
should exit with a non-zero return code, which `dehydrated` will see as an
error and halt. It is then up to the user to fix the relevant issue (e.g. if
the domain name passed as a parameter to `dehydrated` does not exist).

## Credits

Thanks to:

 * David Jones (@drjtwit) for help refactoring code to be more Pythonic.
 * ehuggett for finding and patching an edge-case bug where the ACME challenge
   starts with a hyphen, and providing general thoughts and code.
