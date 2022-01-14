import socket
import sys
import threading
import elgamal


numBits = 32
keyOne = elgamal.generate_keys(iNumBits=numBits, iConfidence=1000)
privKeyB = keyOne["privateKey"]
pubKeyB = keyOne["publicKey"]
print(f"Public Key: {pubKeyB.p} {pubKeyB.g} {pubKeyB.h}")

# ------------------------------------------------------------------------
rendezvous = ('0.0.0.0', 55555)

# connect to rendezvous
print('[WAITING] Connecting to rendezvous server ...')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 50002))
sock.sendto(f"{pubKeyB.p} {pubKeyB.g} {pubKeyB.h}".encode(), rendezvous)

while True:
    data = sock.recv(1024).decode()

    if data.strip() == 'ready':
        print('[WAITING] Checked in with server, waiting ...')
        break

data = sock.recv(1024).decode()
ip, sport, dport , p, g, h= data.split(' ')
sport = int(sport)
dport = int(dport)
p, g, h = map(int, [p,g,h])
pubKeyA = elgamal.PublicKey(p, g, h, iNumBits=numBits)

print('\n[PAIRED]')
print('  Ip Address:          {}'.format(ip))
print('  Source port: {}'.format(sport))
print('  Destination port:   {}\n'.format(dport))

# punch hole
# equiv: echo 'punch hole' | nc -u -p 50001 x.x.x.x 50002
# print('punching hole')

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(('0.0.0.0', sport))
# sock.sendto(b'0', (ip, dport))

print('[READY] Ready to exchange messages!\n')

# listen for
# equiv: nc -u -l 50001
def listen():
#    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#    sock.bind(('0.0.0.0', sport))

    while True:
        data = sock.recv(1024)
        cipher = data.decode()
        print("Received ciphertext: {}".format(cipher))
        print('\rA sent: {}'.format(elgamal.decrypt(privKeyB, cipher)))
        print("________________________________________________________________________________\nB > ", end="")
listener = threading.Thread(target=listen, daemon=True);
listener.start()

# send messages
# equiv: echo 'xxx' | nc -u -p 50002 x.x.x.x 50001
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(('0.0.0.0', dport))

while True:
    msg = input('B > ')
    cipher = elgamal.encrypt(pubKeyA, msg)
    sock.sendto(cipher.encode(), (ip, sport))
