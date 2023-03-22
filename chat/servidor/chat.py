"""
En este módulo se intercambian los mensajes en el chat.
"""


from dataclasses import dataclass
import select
import socket
import threading
import time
from typing import Sequence
from . import servidor
import json

seqsockets = Sequence[socket.socket]

class ChatFormatError(Exception):
    "Representa un error en el formato de intercambio de mensajes."
    def __init__(self, msg: str, payload: bytes|str) -> None:
        self.msg = msg
        self.payload = payload
        super().__init__(self.msg)


@dataclass
class ChatMessage:
    "Encapsula un mensaje."
    user: str
    message: str

    @classmethod
    def from_json(cls, msg: bytes|str) -> "ChatMessage":
        try:
            data = json.loads(msg)
            user = data['user']
            message = data['message']
            assert isinstance(user, str)
            assert isinstance(message, str)
        except (ValueError, KeyError, AssertionError):  # Agrupación de errores
            raise ChatFormatError('Error with the format. Must be a json with the fields "user" and "message". Recommended encoding: utf-8.', msg)
        return cls(user, message)
    
    @property
    def json(self) -> str:
        "Devuelve una cadena en formato json con los datos de la clase."
        return json.dumps({'user': self.user, 'message': self.message})


class Chat(threading.Thread):
    "A partir del servidor gestiona las entradas y salidas del chat."

    def __init__(self, server: servidor.Server, maxbufsize: int = 1024):
        self.server = server
        self._lock = threading.Lock()
        self._end = False
        self._BUFSIZE = maxbufsize
        super().__init__(name='chat')

    @property
    def BUFSIZE(self) -> int:
        "Representa el tamaño máximo del mensaje que puede recibir."
        return self._BUFSIZE

    @property
    def stop(self) -> bool:
        "`True` para detener la ejecución del programa."
        with self._lock:
            return self._end
        
    @stop.setter
    def stop(self, value: bool) -> None:
        with self._lock:
            self._end = value

    def run(self):
        "Actividad del chat."
        assert self.server.is_alive(), "Server must be running before start."
        while not self.stop:
            messages: list[ChatMessage] = []
            r: seqsockets; w: seqsockets; a: seqsockets
            if not self.server.clients:
                time.sleep(0.1)
                continue
            r, w, a = select.select(self.server.clients, self.server.clients, self.server.clients, 1)

            for readable in r:
                data = readable.recv(self.BUFSIZE)
                if data:
                    try:
                        message = ChatMessage.from_json(data)
                        messages.append(message)
                    except ChatFormatError:
                        message = ChatMessage('ServerInfo', "Format Error")
                        messages.append(message)
                else:
                    print("Disconnection from:", readable.getpeername())
                    self.server.clients.remove(readable)
                    readable.close()

            for message in messages:
                print(f"Writting message from {message.user}.")
                for writable in w:
                    writable.sendall(message.json.encode())

            for problem in a:
                print("Disconnection from:", problem.getpeername(), "due a problem.")
                self.server.clients.remove(problem)
                problem.close()
            
            if not self.server.is_alive():
                self.stop = True

