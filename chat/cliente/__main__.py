"""
Aplicación principal.
"""

from . import cliente, interfaz
from typing import Any
from signal import signal, SIGINT
import argparse

def main():
    "Proceso principal del cliente."

    parser = argparse.ArgumentParser(prog='chat.cliente', description='Cliente del chat. Necesita de un servidor para funcionar.')
    parser.add_argument('username', help='Nombre de usuario')
    parser.add_argument('host', nargs='?', default='localhost', help='Dirección IP del servidor')
    parser.add_argument('-p', '--port', default='51000', type=int, help='Puerto del servidor')
    args = parser.parse_args()

    print('-- Sala de chat --')

    client = cliente.Client(host=args.host, port=args.port)
    interface = interfaz.ChatInterface(client, args.username)

    client.start()
    interface.start()

    def _stop(*args: Any):
        "Para los procesos"
        client.stop = True
        interface.stop = True
        print('\nPulsa ahora Enter para salir.')

    signal(SIGINT, _stop)

    client.join()
    interface.join()


if __name__ == '__main__':
    main()