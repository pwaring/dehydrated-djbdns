# letsencrypt.sh-djbdns

Hook script for [letsencrypt.sh](https://github.com/lukas2511/letsencrypt.sh)
with [djbdns](http://cr.yp.to/djbdns.html).

## Dependencies

 * Python 3.x. The hook script will not work in Python 2.x.
 * `dnspython`: Package `python3-dnspython` in Ubuntu.

## Credits

Thanks to David Jones (@drjtwit) for help refactoring the main loop of the
script to be more Pythonic.
