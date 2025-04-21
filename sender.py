import socket
import threading
import json
import math
import time
import logging
import traceback
import argparse
import os

# Configuration RLC-AM
WINDOW_SIZE = 8
SN_MODULUS = 1024
PDU_SIZE = 1000
RETX_TIMEOUT = 1.0  # secondes avant retransmission périodique
HOST, PORT = 'localhost', 8000

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [SENDER] %(levelname)s: %(message)s'
)

class RLCSender:
    def __init__(self, host, port):
        try:
            self.sock = socket.create_connection((host, port))
            logging.info(f"Connected to {host}:{port}")
            self.base = 0
            self.next_sn = 0
            self.segments = {}    # SN -> PDU
            self.lock = threading.Lock()
            self.ack_event = threading.Event()

            # Annonce
            self.sock.sendall(json.dumps({'type':'HELLO','role':'SENDER'}).encode())

            # Démarre écoute des ACKs
            threading.Thread(target=self._listen_acks, daemon=True).start()
            # Démarre boucle de retransmission
            threading.Thread(target=self._retransmit_loop, daemon=True).start()
        except Exception:
            logging.error("Failed to connect or start threads")
            traceback.print_exc()
            raise

    def _listen_acks(self):
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    logging.warning("ACK listener: socket closed by server")
                    break
                status = json.loads(data.decode())
                logging.debug(f"Received STATUS PDU: {status}")
                with self.lock:
                    for sn in status['acks']:
                        if sn in self.segments:
                            del self.segments[sn]
                            logging.info(f"Acked SN {sn}")
                    old_base = self.base
                    self.base = status['new_base']
                    if self.base != old_base:
                        logging.debug(f"Sliding window base -> {self.base}")
                self.ack_event.set()
        except Exception:
            logging.error("Exception in ACK listener")
            traceback.print_exc()

    def _retransmit_loop(self):
        while True:
            time.sleep(RETX_TIMEOUT)
            with self.lock:
                for sn, pdu in list(self.segments.items()):
                    try:
                        self.sock.sendall(pdu)
                        logging.warning(f"Retransmitted SN {sn}")
                    except Exception:
                        logging.error(f"Error retransmitting SN {sn}")
                        traceback.print_exc()

    def send_sdu(self, sdu_bytes):
        # segmentation & ARQ
        total = len(sdu_bytes)
        parts = math.ceil(total / (PDU_SIZE - 8))
        logging.info(f"Sending SDU of {total} bytes in {parts} segments")
        for i in range(parts):
            start = i * (PDU_SIZE - 8)
            seg = sdu_bytes[start:start + (PDU_SIZE - 8)]
            fi = ('01' if i==0 else '00') + ('10' if i==parts-1 else '00')
            sn = self.next_sn
            header = {'sn': sn, 'fi': fi, 'type': 'DATA'}
            pdu = json.dumps({'header': header, 'payload': seg.hex()}).encode()
            self._send_with_arq(sn, pdu)
            self.next_sn = (self.next_sn + 1) % SN_MODULUS
        logging.info("Finished sending SDU")

    def _send_with_arq(self, sn, pdu):
        while True:
            with self.lock:
                win = (self.next_sn - self.base + SN_MODULUS) % SN_MODULUS
                if win < WINDOW_SIZE:
                    try:
                        self.sock.sendall(pdu)
                        self.segments[sn] = pdu
                        logging.debug(f"Sent PDU SN {sn}, window usage {win+1}/{WINDOW_SIZE}")
                    except Exception:
                        logging.error(f"Error sending PDU SN {sn}")
                        traceback.print_exc()
                    break
            self.ack_event.wait(1)
            self.ack_event.clear()
        while True:
            with self.lock:
                if sn not in self.segments:
                    return
            self.ack_event.wait(1)
            self.ack_event.clear()

    def send_file(self, file_path):
        # envoi métadonnées
        basename = os.path.basename(file_path)
        name, ext = os.path.splitext(basename)
        meta = f"{name}|{ext.lstrip('.')}".encode('utf-8')
        logging.info(f"Sending metadata: {name}{ext}")
        self.send_sdu(meta)
        # envoi contenu fichier
        with open(file_path, 'rb') as f:
            data = f.read()
        logging.info(f"Sending file content ({len(data)} bytes)")
        self.send_sdu(data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RLCSender avec fichier')
    parser.add_argument('file', help='Chemin vers le fichier à envoyer')
    args = parser.parse_args()
    sender = RLCSender(HOST, PORT)
    try:
        sender.send_file(args.file)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Sender interrompu et sortie")
