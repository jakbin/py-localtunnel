import os
import sys
from py_localtunnel.tunnel import Tunnel

def run_localtunnel(port: int, subdomain: str):
    t = Tunnel()
    url = t.get_url(subdomain)
    sys.stdout.write(f"Your url is: {url}\n")
    sys.stdout.flush()
    try:
        t.create_tunnel(port)
    except KeyboardInterrupt:
        sys.stdout.write("\nKeyboardInterrupt: Stopping tunnel...\n")
        sys.stdout.flush()

    t.stop_tunnel()
    os._exit(0)
