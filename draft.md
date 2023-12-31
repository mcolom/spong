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

Cada comando es una secuencia de bytes con este formato C\<comando\>\<parámetros\>, donde "C" es el carácter ASCII de la letra C mayúscula y \<comando\> es un byte sin signo (entre 0 y 255). Para facilitar que el MSX pueda decodificar los comandos, las palabras de 16 bits se codifican en _little endian_, es decir, el LSB primero.Por ejemplo, la palabra 0x1234 se codificarían como 0x34, 0x12.

La posición de un jugador se codifica en un byte sin signo, ya que los jugadores solamente se pueden mover en horizontal o vertical. La posición 0 se corresponde a arriba/izquierda.

Comandos:

### PING
El cliente envía un ping al servidor.
- \<num\> = un byte sin signo

### PONG
El servidor envía un pong al servidor, en respuesta a su ping. La respuesta contiene el mismo número enviado en el ping.
- \<num\> = un byte sin signo

### PLAYER\_RENAME
El cliente solicita al servidor un cambio de nombre. Generalmente se utiliza al principio.
- \<mensaje\> = cadena ASCIIZ con el nombre, con un máximo de 8 caracteres.

### BAD\_FORMAT
El cliente o servidor indica a la otra parte que el formato del comando no ha sido reconocido.
- \<mensaje\> = cadena ASCIIZ con el mensaje de error.

### CONN\_REFUSED
El servidor indica a un cliente que su conexión ha sido rechazada, junto con un mensaje explicativo. Por ejemplo, que el servidor ha alcanzado su número máximo de jugadores en la sala de espera.
- \<motivo\> = cadena ASCIIZ. 

### GAME\_START
El servidor notifica a un cliente que ha sido admitido en la partida y le coloca en una portería.
- \<pos\> = caracter ASCII que indica la portería del jugador: "U" (arriba), "D" (abajo), "L" (izquierda) o "R" (derecha).

### GAME\_OVER
El servidor notifica a los clientes que la partida ha terminado y da el nick del ganador.
- \<ganador\> = cadena ASCIIZ con el nick del ganador.

### PLAYERS\_UPDATE
El servidor notifica a un cliente de la posición de los jugadores en la partida.
- \<U\>\<D\>\<L\>\<R\> = las posiciones de los jugadores, en este orden: arriba (U), abajo (D), izquierda (L) o derecha (R). En el caso de que uno jugador haya sido eliminado, el valor correspondiente a su posición es 255.

### GET\_PLAYERS\_QUEUE
El cliente pide al servidor la lista de jugadores en la cola de espera.

Respuesta:
\<lista_de_nicks\> = lista de nicks en la cola de espera. Cada nick está terminado con un byte 0. El terminador de la lista es otro cero.

### WHOS\_PLAYING
El cliente pide al servidor la lista de los jugadores activos en la partida.
La respuesta es una lista de nicks con una longitud entre 0 y 4.
  
Respuesta:
\<lista_de_nicks\> = lista de nicks activos en la partida. El orden indica la portería:  arriba, abajo, izquierda y derecha. Cada nick está terminado con un byte 0. El terminador de la lista es otro cero.

### BALLS\_UPDATE
El servidor notifica a un cliente la posición de las pelotas.
- \<bolas\> = lista de posiciones de pelotas <X><Y>, donde X e Y son las coordenadas horizontales y verticales en la pantalla. El terminador de la lista es el par <255><255>.

### HIT\_NOTIFICATION
El servidor notifica a un cliente que un jugador ha golpeado una pelota. El cliente puede utilizar esta notificación para reproducir sonidos o efectos gráficos.
- \<P\> = portería del jugador que ha golpeado la pelota. Es un carácter entre "U" (arriba), "D" (abajo), "L" (izquierda) o "R" (derecha).

### DEBUG\_TEXT\_MESSAGE
El cliente o el servidor envían un mensaje de texto libre. Se utiliza básicamente para depuración.
- \<msg\> = mensaje de texto ASCIIZ.
