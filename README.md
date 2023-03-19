# Simple Chat

Chat simple creado como base para el ejercicio 7 del [Curso de Python de IEEE 2023](https://github.com/commodoro/CursoPython23). 

## Uso

Para usar el chat debes lanzar antes un servidor con:

```bash
python3 -m chat.server
```

Para empezar a chatear debes hacer:

```bash
python3 -m chat.client usuario [ip_servidor] 
```

Donde `ip_servidor` es la ip del servidor (por defecto es `localhost`).

Puedes ver las opciones de ambos programas añadiendo `--help`.