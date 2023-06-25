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
