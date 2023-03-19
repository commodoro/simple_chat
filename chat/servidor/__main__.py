"""
Aplicación principal
"""

from typing import Any
from signal import signal, SIGINT
import argparse
from . import chat, servidor


def main():
    "Función principal"

    parser = argparse.ArgumentParser(prog='chat.server', description="Servidor para chatear.")
    parser.add_argument('-l', '--local', action='store_true', help='Incluir para que solo sea visible desde el equipo.')
    parser.add_argument('-p', '--port', help='Puerto del servidor', type=int, default=51000)
    args = parser.parse_args()

    server = servidor.Server(host='localhost' if args.local else '', port=args.port)
    chatroom = chat.Chat(server)

    print('Iniciando servidor.')

    server.start()
    chatroom.start()

    print('Ok. Todo listo. Esperando mensajes.')

    def _stop(*args: Any):
        "Para los procesos"
        server.stop = True
        chatroom.stop = True
        print('\nSaliendo')

    signal(SIGINT, _stop)

    server.join()
    chatroom.join()

if __name__ == '__main__':
    main()