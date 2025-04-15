#!/usr/bin/env python3
import sys
import os
import socketio
import numpy as np
import threading
import time

# Configuration
SERVER_URL = 'http://localhost:3000/rlc'
PACKET_SIZE = 1024      # taille d'un paquet original en octets
FIELD_SIZE = 256        # GF(2^8)
K = None                # nombre de paquets originaux (sera calculé)

# Préparer tables GF(2^8)
EXP = np.zeros(512, dtype=int)
LOG = np.zeros(256, dtype=int)
def init_gf():
    x = 1
    for i in range(255):
        EXP[i] = x
        LOG[x] = i
        x ^= (x << 1) ^ (0x1d if x & 0x80 else 0)
        x &= 0xFF
    # Répéter les 255 premiers éléments aux positions 255..509
    EXP[255:510] = EXP[:255]

init_gf()

def gf_add(a, b): return a ^ b
def gf_mul(a, b):
    return EXP[LOG[a] + LOG[b]] if a and b else 0

def random_vector(k):
    return np.random.randint(1, FIELD_SIZE, size=k, dtype=int)

def encode_packet(packets, g):
    coded = np.zeros(PACKET_SIZE, dtype=int)
    for i, pkt in enumerate(packets):
        pkt_array = np.frombuffer(pkt, dtype=np.uint8)
        coded = [gf_add(c, gf_mul(g[i], x)) for c, x in zip(coded, pkt_array)]
    return bytes(coded)



# Lire et découper le fichier
def load_file(path):
    data = open(path, 'rb').read()
    packets = []
    for i in range(0, len(data), PACKET_SIZE):
        chunk = data[i:i+PACKET_SIZE]
        # Si chunk est plus petit, on le pad avec des zéros
        if len(chunk) < PACKET_SIZE:
            chunk = chunk + bytes(PACKET_SIZE - len(chunk))
        packets.append(chunk)
    return packets


# Socket.IO client
sio = socketio.Client()

@sio.event(namespace='/rlc')
def connect():
    print('✅ Connecté au serveur (sender)')
    # Envoi immédiat des métadonnées
    sio.emit('metadata', {
        'size': os.path.getsize(path),
        'num_packets': len(packets)
    }, namespace='/rlc')

@sio.on('ack', namespace='/rlc')
def on_ack(data=None):
    print('🔔 ACK reçu, arrêt de l\'envoi.')
    th.stop()
    sio.disconnect()

def send_loop(packets):
    global K
    K = len(packets)
    sent = 0
    while sio.connected:
        g = random_vector(K)
        coded = encode_packet(packets, g)
        pkt = {
            'coeffs': g.tolist(),
            'data': list(coded)
        }
        sio.emit('send_packet', pkt, namespace='/rlc')
        sent += 1
        print(f'➡️ Paquet codé #{sent} envoyé')
        time.sleep(0.01)  # ajuster le débit si besoin

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python sender.py /chemin/vers/image.jpg')
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print('❌ Fichier non trouvé:', path)
        sys.exit(1)

    packets = load_file(path)
    print(f'🔢 {len(packets)} paquets originaux prêts.')
    
    # Démarrage de l’envoi
    threading.Thread(target=send_loop, args=(packets,), daemon=True).start()


    sio.connect(SERVER_URL, namespaces=['/rlc'])
    # Après sio.connect(...)
    #sio.emit('metadata', { 'size': os.path.getsize(path), 'num_packets': len(packets) })

    # Démarrer l’envoi dans un thread pour pouvoir recevoir l’ACK
    th = threading.Thread(target=send_loop, args=(packets,), daemon=True)
    th.start()
    sio.wait()
