import socket
import threading
import json
import time
import logging
import traceback

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
            # Annonce
            self.sock.sendall(json.dumps({'type':'HELLO','role':'RECEIVER'}).encode())
            threading.Thread(target=self._receive_loop, daemon=True).start()
        except Exception:
            logging.error("Failed to connect or start receive loop")
            traceback.print_exc()
            raise

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
                # Traiter les buffered
                while self.expected_sn in self.buffer:
                    buffered = self.buffer.pop(self.expected_sn)
                    self._deliver(buffered)
                    self.expected_sn = (self.expected_sn + 1) % SN_MODULUS
            self._send_status()

    def _deliver(self, msg):
        payload = bytes.fromhex(msg['payload'])
        self.out_sdu.extend(payload)
        fi = msg['header']['fi']
        logging.info(f"Delivered SN {msg['header']['sn']} payload {len(payload)} bytes")
        if fi.endswith('10'):
            logging.info(f"Complete SDU reçu ({len(self.out_sdu)} bytes): {self.out_sdu}")
            self.out_sdu.clear()

    def _send_status(self):
        new_base = self.expected_sn
        # ACKs possibles (simplification : tous avant new_base)
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
