import os
import socket
import queue
import threading
from py_localtunnel.get_assigned_url import get_assigned_url, AssignedUrlInfo
from urllib.parse import urlparse, urlsplit

LOCAL_TUNNEL_SERVER = "http://localtunnel.me/"
Debug = True

class TunnelConn:
    def __init__(self, remote_host: str, remote_port: int, local_port: int):
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.local_port = local_port
        self.remote_conn = None
        self.local_conn = None
        self.error_channel = None

    def tunnel(self, reply_ch):
        self.error_channel = [] # clear previous channel's message
        try:
            remote_conn = self.connect_remote()
            local_conn = self.connect_local()
            self.remote_conn = remote_conn
            self.local_conn = local_conn
            thread_1 = threading.Thread(target=self.copy_data, args=(remote_conn, local_conn))
            thread_2 = threading.Thread(target=self.copy_data, args=(local_conn, remote_conn))
            thread_1.start()
            thread_2.start()
            thread_1.join()
            thread_2.join()
        except Exception as e:
            if Debug:
                print(f"Stop copy data! error=[{e}]")
        finally:
            if self.remote_conn:
                self.remote_conn.close()
            if self.local_conn:
                self.local_conn.close()
            reply_ch.put(1)

    def stop_tunnel(self):
        if self.remote_conn:
            self.remote_conn.close()
        if self.local_conn:
            self.local_conn.close()

    def connect_remote(self):
        remote_addr = (self.remote_host, self.remote_port)
        proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
        if proxy:
            proxy_url = urlparse(proxy)
            remote_conn = socket.create_connection(proxy_url.netloc.split(':'))
            connect_request = f"CONNECT {self.remote_host}:{self.remote_port} HTTP/1.1\r\nHost: {self.remote_host}\r\n\r\n"
            remote_conn.sendall(connect_request.encode())
            response = remote_conn.recv(4096)
            if response.startswith(b'HTTP/1.1 200'):
                return remote_conn
            else:
                raise Exception(f"Failed to connect via proxy: {response}")
        else:
            return socket.create_connection(remote_addr)

    def connect_local(self):
        local_addr = ('localhost', self.local_port)
        return socket.create_connection(local_addr)

    def copy_data(self, source, destination):
        e = None  # initialize e to None
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break
                destination.sendall(data)
        except Exception as ex:
            if Debug:
                print(f"Stop copy data! error=[{ex}]")
            e = ex  # assign the exception to e
        finally:
            if self.error_channel is not None and e is not None:
                self.error_channel.append(e)


class Tunnel:
    def __init__(self):
        self.assigned_url_info = None
        self.local_port = None
        self.tunnel_conns = []
        self.cmd_chan = queue.Queue()

    def start_tunnel(self) -> None:
        self.check_local_port()
        reply_ch = queue.Queue(maxsize=self.assigned_url_info.max_conn_count)
        remote_host = urlsplit(LOCAL_TUNNEL_SERVER).netloc
        for _ in range(self.assigned_url_info.max_conn_count):
            tunnel_conn = TunnelConn(remote_host, self.assigned_url_info.port, self.local_port)
            self.tunnel_conns.append(tunnel_conn)
            thread = threading.Thread(target=tunnel_conn.tunnel, args=(reply_ch,))
            thread.start()
        while reply_ch.qsize() < self.assigned_url_info.max_conn_count:
            cmd = self.cmd_chan.get()
            if cmd == 'STOP':
                break

    def stop_tunnel(self) -> None:
        if Debug:
            print(f" Info: Stop tunnel for localPort[{self.local_port}]!")
        self.cmd_chan.put('STOP')
        for tunnel_conn in self.tunnel_conns:
            tunnel_conn.stop_tunnel()

    def get_url(self, assigned_domain: str) -> str:
        if not assigned_domain:
            assigned_domain = "?new"
        assigned_url_info = get_assigned_url(assigned_domain)
        self.assigned_url_info = AssignedUrlInfo(**assigned_url_info.__dict__)
        self.tunnel_conns = []
        return self.assigned_url_info.url

    def create_tunnel(self, local_port: int) -> None:
        self.local_port = local_port
        self.start_tunnel()
    
    def check_local_port(self):
        try:
            with socket.create_connection(('localhost', self.local_port)) as sock:
                pass
        except ConnectionRefusedError:
            print(' Error: Cannot connect to local port')   
            os._exit(0)   
