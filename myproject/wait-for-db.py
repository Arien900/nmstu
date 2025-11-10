import sys
import time
import socket

host, port = sys.argv[1].split(':')
port = int(port)

print(f"Ожидание PostgreSQL на {host}:{port}...")

while True:
    try:
        sock = socket.create_connection((host, port), timeout=1)
        sock.close()
        break
    except (socket.timeout, ConnectionRefusedError):
        time.sleep(1)

print("PostgreSQL готов.")