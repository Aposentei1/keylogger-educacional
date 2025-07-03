# Keylogger Educacional 🧠💻

⚠️ Este projeto é apenas para fins educacionais e testes locais. **Não utilize este código para qualquer atividade ilegal ou sem consentimento**.

Este é um exemplo de keylogger feito com Python que:
- Captura pressionamento de teclas
- Criptografa com AES
- Envia via WebSocket
- (Opcional) Inicia com o sistema Windows



este repositório contém dois componentes principais:

- **Cliente (keylogger.py):** captura teclas, criptografa e envia via WebSocket para o servidor.  
- **Servidor (server.py):** servidor Flask com Socket.IO que recebe, descriptografa e salva os logs.


## Instalação keylogger

 Instale o PyInstaller : pip install pyinstaller
 
 Comando para criar um .EXE que não abre janela (CMD) e você pode adicionar seu ícone:

 pyinstaller --onefile --noconsole --icon=seu_icone.ico keylogger.py

 o .EXE estará aqui dist/keylogger.exe

## rodar server.py no terminal:
pip install flask flask-socketio cryptography

python server.py


