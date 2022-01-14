import socket
import sys
import threading
import elgamal 


numBits = 32
keyOne = elgamal.generate_keys(iNumBits=numBits,iConfidence=1000)
privKeyA = keyOne["privateKey"]
pubKeyA = keyOne["publicKey"]
print(f"Public Key: {pubKeyA.p} {pubKeyA.g} {pubKeyA.h}")

#------------------------------------------------------------------------
rendezvous = ('0.0.0.0', 55555)

# connect to rendezvous
print('[WAITING] Connecting to Rendezvous server ...')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 50001))
sock.sendto(f"{pubKeyA.p} {pubKeyA.g} {pubKeyA.h}".encode(), rendezvous)

while True:
    data = sock.recv(1024).decode()

    if data.strip() == 'ready':
        print('[WAITING] Checked in with server, waiting ...')
        break

data = sock.recv(1024).decode()
ip, sport, dport, p, g, h = data.split(' ')
sport = int(sport)
dport = int(dport)
p, g, h = map(int, [p,g,h])
pubKeyB = elgamal.PublicKey(p, g, h, iNumBits=numBits)

print('\n[Paired]')
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
        print('\rB > {}'.format(elgamal.decrypt(privKeyA, cipher)))
        print("________________________________________________________________________________\nA > ",end="")

listener = threading.Thread(target=listen, daemon=True);
listener.start()

# send messages 
# equiv: echo 'xxx' | nc -u -p 50002 x.x.x.x 50001
#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.bind(('0.0.0.0', dport))

while True:
    msg = input('A > ')
    cipher = elgamal.encrypt(pubKeyB, msg)
    sock.sendto(cipher.encode(), (ip, sport))
