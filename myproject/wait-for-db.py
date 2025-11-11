#!/usr/bin/env python3
import socket
import time
import sys

host, port = sys.argv[1].split(':')
port = int(port)

print("⏳ Ожидание PostgreSQL...")
while True:
    try:
        with socket.create_connection((host, port), timeout=1):
            break
    except (socket.timeout, ConnectionRefusedError):
        time.sleep(1)
print("Готово.")