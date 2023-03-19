"""
Contiene la clase `Server` encarga de las conexiones.
"""

import select
import threading
import socket

class Server(threading.Thread):
    "Se encarga de gestionar los sockets entrantes"
    
    def __init__(self, *, host: str, port: int, maxbufsize: int = 1024):
        self.host = host
        self.port = port
        self._clients : list[socket.socket] = []
        self._lock = threading.Lock()
        self._end = False
        super().__init__(name="Chat Server")

    @property
    def clients(self) -> list[socket.socket]:
        "Clientes que se han conectado al socket"
        with self._lock:
            return self._clients
        
    @property
    def stop(self) -> bool:
        "`True` para detener la ejecución del programa."
        with self._lock:
            return self._end
        
    @stop.setter
    def stop(self, value: bool) -> None:
        with self._lock:
            self._end = value

    def clear_clients(self):
        "Elimina todas las conexiones."
        with self._lock:
            for client in self._clients:
                client.close()
            self._clients.clear()

    def run(self) -> None:
        "Comprueba el socket del servidor y gestiona las nuevas conexiones."
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen(0)
            while not self.stop:
                ready: list[socket.socket]
                ready, *_ = select.select((s,),(),(), 1)
                if ready:
                    client, address = ready[0].accept()
                    print("New connection from:", client.getpeername())
                    self.clients.append(client)
            self.clear_clients()


