## Slowloris DOS Attack

This script abuses the CVE-2007-6750 vulnerability. The script exploits this vulnerability using one machine by creating multiple threads and sending from each thread incomplete requests thus overloading the server and making the website unreachable.
    

### Usage
    $ ./slowloris.py example.com
    $ ./slowloris.py example.com:443
    $ ./slowloris.py 192.168.1.1
    $ ./slowloris.py 192.168.1.1:443
