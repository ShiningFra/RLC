#!/usr/bin/env python3
import sys
import socketio
import numpy as np
import threading

# Configuration (doit correspondre au sender)
SERVER_URL = 'http://localhost:3000/rlc'
PACKET_SIZE = 1024

# Variables globales pour métadonnées
original_size = None  # taille réelle du fichier en octets
K = None              # nombre de paquets

# Tables GF
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

# Gauss-Jordan pour décoder
def gauss_jordan(A, B):
    A = A.copy().astype(int)
    B = B.copy().astype(int)
    n, k = A.shape
    rank = 0
    for col in range(k):
        piv = np.where(A[rank:,col]!=0)[0]
        if piv.size == 0 or rank>=n: continue
        piv = piv[0] + rank
        A[[rank,piv]] = A[[piv,rank]]
        B[[rank,piv]] = B[[piv,rank]]
        inv = EXP[255 - LOG[A[rank,col]]]
        A[rank] = [ gf_mul(x, inv) for x in A[rank] ]
        B[rank] = [ gf_mul(x, inv) for x in B[rank] ]
        for i in range(n):
            if i!=rank and A[i,col]!=0:
                factor = A[i,col]
                A[i] = [ gf_add(A[i,j], gf_mul(factor, A[rank,j])) for j in range(k) ]
                B[i] = [ gf_add(B[i,j], gf_mul(factor, B[rank,j])) for j in range(B.shape[1]) ]
        rank += 1
        if rank==k: break
    return B if rank==k else None

# Stockage des paquets reçus
coeffs_list = []
data_list = []

sio = socketio.Client()

@sio.event(namespace='/rlc')
def connect():
    print('✅ Connecté au serveur (receiver)')

# Réception des métadonnées (taille et nombre de paquets)
@sio.on('metadata', namespace='/rlc')
def on_metadata(meta):
    global original_size, K
    original_size = meta['size']
    K = meta['num_packets']
    print(f'ℹ️ Métadonnées reçues → taille: {original_size} octets, paquets: {K}')

@sio.on('packet', namespace='/rlc')
def on_packet(pkt):
    global coeffs_list, data_list, K
    if K is None:
        print('⚠️ En attente des métadonnées avant de traiter les paquets')
        return

    g = np.array(pkt['coeffs'], dtype=int)
    d = np.array(pkt['data'], dtype=int)
    if len(coeffs_list) < K:
        coeffs_list.append(g)
        data_list.append(d)
        print(f'⬅️ Paquet reçu #{len(coeffs_list)} / {K}')
        # tenter décodage si possible
        if len(coeffs_list) == K:
            A = np.stack(coeffs_list)
            B = np.stack(data_list)
            sol = gauss_jordan(A, B)
            if sol is not None:
                print('✅ Décodage réussi ! Reconstruction du fichier.')
                # écrire le fichier complet avec padding
                with open('reconstructed_padded.bin', 'wb') as f:
                    for row in sol:
                        f.write(bytes(row.tolist()))
                # retirer le padding
                with open('reconstructed_padded.bin', 'rb') as fin, \
                     open('reconstructed.bin', 'wb') as fout:
                    data = fin.read(original_size)
                    fout.write(data)
                print('📁 Fichier reconstruit en reconstructed.bin')
                # ACK pour stopper le sender
                sio.emit('ack', namespace='/rlc')
                sio.disconnect()

if __name__ == '__main__':
    sio.connect(SERVER_URL, namespaces=['/rlc'])
    sio.wait()
