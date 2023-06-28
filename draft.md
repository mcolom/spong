# Borrador del Bob SPong
Este documento es una descripción de cómo es el juego, para tener una idea antes de implementar nada.

## Sala de espera
El jugador inicia el juego y el programa le pide un nick.
Si el nick ya está en uso, repite la pregunta hasta que se obtenga un nick válido.
El servidor no reserva nicks, se utilizará el que le de el usuario al entrar.

Hay un número máximo de conexiones de jugadores al servidor, que se añaden a una cola.
El juego se inicia cuando hay al menos dos jugadores en la cola. El servidor va metiendo en el juego a los participantes en cola, con un mínimo de dos y un máximo de cuatro.

Los jugadores en la cola pueden ver la partida en curso mientras esperan tu turno y escribir mensajes que serán mostrados en el área de notificaciones del juego.

## El juego
La pantalla se divide en dos zonas.
La zona superior contiene una línea con mensajes del servidor, como por ejemplo:
* Notificación de que un nuevo jugador entra en el juego
* Notificación de que un nuevo jugador entra en la cola de espera
* Posición en la cola de un jugador (mensaje solamente para ese participante)
* Notificación de que un jugador ha sido eliminado
* Cualquier otro mensaje del servidor

El resto de la pantalla es la zona de juego.
Cuatro raquetas (arriba, abajo, izquierda, derecha) juegan el partido de Pong.
El ángulo del rebote de la pelota dependen del punto en el que golpea la raqueta. La velocidad de la pelota depende del número de rebotes acumulados.
Las pelotas pueden rebotar entre ellas, cambiando su dirección de forma aleatoria.

Cuando la pelota queda detrás de la raqueta, el jugador queda eliminado y vuelve al final de la cola.
Si la conexión con el jugador se pierde, queda eliminado.

Para hacer el juego más divertido, aleatoriamente aparecerán obstáculos móviles que dispararán una pelota adicional al ser alcanzados.

## Comunicación clientes/servidor
El juego está centralizado a un único servidor, al que los jugadores se conectan como clientes via TCP/IP.
Una vez establecido el canal de comunicación, el servidor y los clientes intercambian actualizaciones de estado. La comunicación es siempre entre un cliente y el servidor.

Cada comando es una secuencia de bytes con este formato C<num_comando><parámetros_del_comando>, donde "C" es el carácter ASCII de la letra C mayúscula y <num_comando> es un byte sin signo (entre 0 y 255). Para facilitar que el MSX pueda decodificar los comandos, las palabras de 16 bits se codifican en _little endian_, es decir, el LSB primero.Por ejemplo, la palabra 0x1234 se codificarían como 0x34, 0x12. 

Comandos:

### Formato incorrecto
El cliente o servidor indica a la otra parte que el formato del comando no ha sido reconocido.
- <num_comando> = 1

### Conexión rechazada
Indica a un cliente que su conexión ha sido rechazada, junto con un mensaje explicativo. Por ejemplo, que el servidor ha alcanzado su número máximo de jugadores en la sala de espera.
- <num_comando> = 2
- <motivo> = cadena ASCIIZ. 

### Inicio de partida
El servidor notifica a los clientes que comienza una nueva partida
- <num_comando> = 3

### Fin de partida
- <num_comando> = 4
- <ganador> = cadena ASCIIZ con el nick del ganador.
El servidor notifica a los clientes que comienza una nueva partida

### Inicilización jugador
El servidor inicializa un nuevo jugador después de que entre en la partida
- <num_comando> = 5
- <ID> = ID que se le asigna al jugador (byte)
- <portería> = arriba (1), abajo (2), derecha (3), izquierda (4)
- <posición> = byte con la posición del jugador. La posición 0 ecorresponde a arriba y a la izquierda.


