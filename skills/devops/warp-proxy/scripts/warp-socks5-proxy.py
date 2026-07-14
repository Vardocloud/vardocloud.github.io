import socket
import struct
import select
import os
import sys

SOCKS_VERSION = 5
WARP_MARK = 1  # fwmark for WARP routing (ip rule fwmark 1 lookup 100)

def set_mark(sock):
    """SO_MARK=1 routes packet through WARP WireGuard interface.
    Requires CAP_NET_ADMIN (proxy must run as root)."""
    try:
        sock.setsockopt(socket.SOL_SOCKET, 36, WARP_MARK)  # SO_MARK = 36
    except PermissionError:
        print("ERROR: SO_MARK requires CAP_NET_ADMIN. Run as root.", file=sys.stderr)
        raise

def handle_client(client):
    remote = None
    try:
        # SOCKS5 handshake
        client.recv(1)  # version
        nmethods = ord(client.recv(1))
        for _ in range(nmethods):
            client.recv(1)  # methods
        client.sendall(struct.pack("!BB", SOCKS_VERSION, 0))  # no auth
        
        # Request
        data = b''
        while len(data) < 4:
            data += client.recv(4 - len(data))
        ver, cmd, _, atyp = struct.unpack("!BBBB", data)
        
        addr = None
        if atyp == 1:  # IPv4
            addr = socket.inet_ntoa(client.recv(4))
        elif atyp == 3:  # Domain
            addr_len = ord(client.recv(1))
            addr = client.recv(addr_len).decode()
        else:
            client.close()
            return
        
        port = struct.unpack("!H", client.recv(2))[0]
        
        if cmd != 1:  # CONNECT only
            client.close()
            return
        
        # Connect via WARP
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        set_mark(remote)
        remote.settimeout(10)
        remote.connect((addr, port))
        
        # Reply success
        bind_addr = b'\x00\x00\x00\x00'
        bind_port = struct.pack("!H", 0)
        client.sendall(struct.pack("!BBBB", SOCKS_VERSION, 0, 0, 1) + bind_addr + bind_port)
        
        # Relay
        sockets = [client, remote]
        while True:
            r, _, _ = select.select(sockets, [], [], 60)
            if not r:
                break
            for s in r:
                data = s.recv(8192)
                if not data:
                    return
                if s is client:
                    remote.sendall(data)
                else:
                    client.sendall(data)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        try: client.close()
        except: pass
        try: remote.close()
        except: pass

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 1080))
    server.listen(10)
    print("WARP SOCKS5 proxy on 127.0.0.1:1080", flush=True)
    
    while True:
        client, addr = server.accept()
        pid = os.fork()
        if pid == 0:
            handle_client(client)
            os._exit(0)
        else:
            client.close()

if __name__ == '__main__':
    main()
