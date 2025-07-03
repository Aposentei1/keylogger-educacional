from flask import Flask
from flask_socketio import SocketIO, emit
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

app = Flask(__name__)
socketio = SocketIO(app)
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
backend = default_backend()

def decrypt_text(ct_b64, key_b64, iv_b64):
    ct = base64.b64decode(ct_b64)
    key = base64.b64decode(key_b64)
    iv = base64.b64decode(iv_b64)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ct) + decryptor.finalize()
    return decrypted.decode('utf-8', errors='ignore')

@socketio.on('send_log')
def handle_send_log(data):
    ip = data.get("ip_local", "unknown")
    log_encrypted = data.get("log_encrypted")
    key = data.get("key")
    iv = data.get("iv")

    if not all([ip, log_encrypted, key, iv]):
        emit('error', {'error': 'Dados incompletos'})
        return

    try:
        log_text = decrypt_text(log_encrypted, key, iv)
        filename = os.path.join(log_folder, f"{ip}.txt")
        with open(filename, "a", encoding="utf-8") as f:
            f.write(log_text + "\n")

        emit('log_received', {'message': f'Log recebido de {ip}', 'log': log_text}, broadcast=True)
    except Exception as e:
        emit('error', {'error': str(e)})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
