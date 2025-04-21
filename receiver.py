import socket
import threading
import json
import time
import logging
import traceback
import os
import sys

# Configuration RLC-AM
SN_MODULUS = 1024
WINDOW_SIZE = 8
HOST, PORT = 'localhost', 8000

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [RECEIVER] %(levelname)s: %(message)s'
)

class RLCReceiver:
    def __init__(self, host, port):
        try:
            self.sock = socket.create_connection((host, port))
            logging.info(f"Connected to {host}:{port}")
            self.expected_sn = 0
            self.buffer = {}
            self.out_sdu = bytearray()
            self.lock = threading.Lock()
            self.metadata_received = False
            self.filename = None
            self.extension = None

            # Annonce
            self.sock.sendall(json.dumps({'type':'HELLO','role':'RECEIVER'}).encode())
            threading.Thread(target=self._receive_loop, daemon=True).start()
        except Exception:
            logging.error("Failed to connect or start receive loop")
            traceback.print_exc()
            sys.exit(1)

    def _receive_loop(self):
        try:
            while True:
                data = self.sock.recv(4096)
                if not data:
                    logging.warning("Receive loop: socket closed by server")
                    break
                try:
                    msg = json.loads(data.decode())
                except Exception:
                    logging.error("Invalid JSON received")
                    continue
                if msg.get('header', {}).get('type') == 'DATA':
                    self._handle_data(msg)
        except Exception:
            logging.error("Exception in receive loop")
            traceback.print_exc()
        finally:
            self.sock.close()

    def _handle_data(self, msg):
        sn = msg['header']['sn']
        fi = msg['header']['fi']
        logging.debug(f"Received PDU SN {sn}, FI={fi}")
        with self.lock:
            if sn != self.expected_sn:
                self.buffer[sn] = msg
                logging.info(f"Buffered out-of-order SN {sn}")
            else:
                self._deliver(msg)
                self.expected_sn = (self.expected_sn + 1) % SN_MODULUS
                while self.expected_sn in self.buffer:
                    buffered = self.buffer.pop(self.expected_sn)
                    self._deliver(buffered)
                    self.expected_sn = (self.expected_sn + 1) % SN_MODULUS
            self._send_status()

    def _deliver(self, msg):
        # Récupère les données
        payload = bytes.fromhex(msg['payload'])
        self.out_sdu.extend(payload)
        logging.info(f"Delivered SN {msg['header']['sn']} payload chunk ({len(payload)} bytes)")
        # Si fin de SDU
        if msg['header']['fi'].endswith('10'):
            if not self.metadata_received:
                # Premier SDU = métadonnées
                meta_str = self.out_sdu.decode('utf-8')
                parts = meta_str.split('|', 1)
                if len(parts) != 2:
                    logging.error(f"Invalid metadata format: {meta_str}")
                    sys.exit(1)
                self.filename, self.extension = parts
                self.metadata_received = True
                logging.info(f"Metadata received: filename='{self.filename}', extension='{self.extension}'")
            else:
                # Contenu du fichier
                out_name = f"{self.filename}_received.{self.extension}"
                try:
                    with open(out_name, 'wb') as f:
                        f.write(self.out_sdu)
                    logging.info(f"File saved: {out_name} ({len(self.out_sdu)} bytes)")
                except Exception:
                    logging.error(f"Failed to write file: {out_name}")
                    traceback.print_exc()
                # Affichage et sortie
                print(f"contenu enregistré dans {out_name}")
                sys.exit(0)
            # Réinitialise pour SDU suivant
            self.out_sdu.clear()

    def _send_status(self):
        new_base = self.expected_sn
        acks = [(new_base - i - 1) % SN_MODULUS for i in range(min(WINDOW_SIZE, new_base))]
        status_pdu = {'type':'STATUS','new_base': new_base, 'acks': acks}
        try:
            self.sock.sendall(json.dumps(status_pdu).encode())
            logging.debug(f"Sent STATUS new_base={new_base}, acks={acks}")
        except Exception:
            logging.error("Error sending STATUS PDU")
            traceback.print_exc()

if __name__ == '__main__':
    receiver = RLCReceiver(HOST, PORT)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Receiver interrupted and exiting")
        sys.exit(0)
