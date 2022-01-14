import socket
import math


known_port = 50003

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 55555))

while True:
    clients = []
    keyList = {}
    while True:
        data, address = sock.recvfrom(1024)
        print(data.decode())
        p, g, h = map(int, data.decode().split(" "))

        print('connection from: {}'.format(address))
        clients.append(address)
        keyList[address] = (p, g, h)
        print(f"Address: {address}, Public Key: {p}, {g}, {h}")
        sock.sendto(b'ready', address)

        if len(clients) == 2:
            print('got 2 clients, sending details to each')
            break

    c1 = clients.pop()
    c1_addr, c1_port = c1
    p1, g1, h1 = keyList[c1]

    c2 = clients.pop()
    c2_addr, c2_port = c2
    p2, g2, h2 = keyList[c2]

    sock.sendto('{} {} {} {} {} {}'.format(c1_addr, c1_port, c2_port, p1, g1, h1).encode(), c2)
    sock.sendto('{} {} {} {} {} {}'.format(c2_addr, c2_port, c1_port, p2, g2, h2).encode(), c1)
