"""
Define la clase Cliente que gesiona las conexiones con el servidor.
"""

import select
import socket
import threading
import queue

class Client(threading.Thread):
    "Gestiona la conexión con el servidor."

    def __init__(self, *, host: str, port: int, maxbufsize = 1024):
        self.host = host
        self.port = port
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self._lock = threading.Lock()
        self._end = False
        self._BUFSIZE = maxbufsize
        super().__init__(name="chat_client")

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
        "Escanea la conexión en busca de nuevos mensajes y escribe los mensajes de la cola."
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
            conn.connect((self.host, self.port))
            while not self.stop:
                ready : list[socket.socket]
                ready, *_ = select.select((conn,), (), (), 0.2)
                if ready:
                    raw_data = ready[0].recv(self.BUFSIZE)
                    if raw_data:
                        self.input_queue.put(raw_data)
                    else:
                        print('¡Servidor desconectado!')
                        self.stop = True
                        continue
                try:
                    output_data = self.output_queue.get_nowait()
                except queue.Empty:
                    continue
                conn.sendall(output_data)

        

