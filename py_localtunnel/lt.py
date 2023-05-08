import os
from py_localtunnel.tunnel import Tunnel

def run_localtunnel(port: int, subdomain: str):
    t = Tunnel()
    url = t.get_url(subdomain)
    print(f" your url is: {url}")
    try:
        t.create_tunnel(port)
    except KeyboardInterrupt:
        print("\n KeyboardInterrupt: stopping tunnel")

    t.stop_tunnel()
    os._exit(0)