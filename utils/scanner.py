import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

PORT = 8765
TIMEOUT = 0.5

def get_local_network():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    network = ipaddress.ip_network(local_ip + "/24", strict=False)
    return network

def scan(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    try:
        if s.connect_ex((str(ip), PORT)) == 0:
            print(f"[OPEN] {ip}:{PORT}")
    finally:
        s.close()

if __name__ == "__main__":
    network = get_local_network()
    print(f"Scanning {network}...")

    with ThreadPoolExecutor(max_workers=100) as executor:
        for ip in network.hosts():
            executor.submit(scan, ip)