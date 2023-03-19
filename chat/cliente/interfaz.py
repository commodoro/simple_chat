"""
Este módulo se encarga de gestionar los mensajes y mostrarlos por pantalla. También recoge los datos desde la terminal..
"""

from dataclasses import dataclass
import json
from queue import Empty
import threading
from . import cliente

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
    
    @property
    def display(self) -> str:
        "Devuelve como se muestra el mensaje en la terminal."
        return f'[{self.user}]: {self.message}'


class ChatInterface(threading.Thread):
    "Interfaz del chat"

    def __init__(self, client: cliente.Client, username: str):
        self.client = client
        self._end = False
        self._lock = threading.Lock()
        self.user = username
        super().__init__(name='chat_interface')
        
    @property
    def stop(self) -> bool:
        "`True` para detener la ejecución del programa."
        with self._lock:
            return self._end
        
    @stop.setter
    def stop(self, value: bool) -> None:
        with self._lock:
            self._end = value


    def input_method(self):
        "Hilo que captura la entrada desde la terminal."
        while not self.stop:
            entry = input()
            if entry == '.q':
                self.stop = True
                self.client.stop = True
            else:
                message = ChatMessage(self.user, entry)
                self.client.output_queue.put(message.json.encode())

    def run(self):
        "Muestra y recibe los mensajes desde la terminal."

        input_thread = threading.Thread(target=self.input_method, name='input_method')
        input_thread.start()
        while not self.stop:
            try:
                data = self.client.input_queue.get(timeout=0.2)
                message = ChatMessage.from_json(data)
            except Empty:
                if not self.client.is_alive():
                    self.stop = True
                    print('Se ha producido un error. Pulsa enter para salir.')
                continue
            except ChatFormatError:
                print("SysInfo - Bad message from the server")
            else:
                print(message.display)
        input_thread.join()
