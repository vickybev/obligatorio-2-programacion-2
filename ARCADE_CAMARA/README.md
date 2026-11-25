# La casita de los hechizos

Prototipo local para explorar un juego controlado por cámara. El menú tiene
cuatro minijuegos en una primera versión jugable.

## Abrir y jugar

Desde esta carpeta, prepará un entorno de Python 3.12:

~~~powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
~~~

En Windows, podés hacer doble clic en ABRIR_JUEGO.cmd. Si encuentra el entorno del curso lo reutiliza. En una descarga nueva, pide Python 3.12 con el lanzador py y descarga las dependencias la primera vez. Mostrá una mano completa con luz de frente.

- Mové la mano con pulgar e índice separados para desplazar la criatura.
- Juntalos sobre la tarjeta del primer juego para entrar. El mouse y Enter
  también permiten navegar el menú.
- Acercá la boca a un bichito amarillo y cerrá la pinza para atraparlo.
- Mantené los dedos juntos y llevá la presa a la madriguera de abajo a la derecha.
- Abrí la pinza dentro del nido para entregar. Soltar afuera libera al bichito.
- Tenés siete segundos para transportar cada presa y sesenta para juntar ocho.
- Los violetas con cuernos restan cuatro segundos cuando los mordés.
- Cuando la cámara pierde la mano, la partida detiene su tiempo hasta detectarla.
- P pausa, Esc vuelve al menú y Esc desde el menú cierra. La cruz también cierra.
- El mouse y el teclado permiten navegar. Para jugar cualquiera de las cuatro aventuras necesitás la cámara y una mano detectable.

Para seleccionar otra cámara, ejecutá desde esta carpeta con el Python del curso
`main.py --camera 1`.

## Detección

Jugá con luz frontal y un fondo simple. Ajustá la distancia hasta que se vea la mano completa, con espacio para moverla sin salir del cuadro. C abre la guía de cámara. Si la mano deja de detectarse, se pausa la partida hasta recuperarla.

## Recursos y uso de IA

Los sonidos se sintetizaron para el proyecto con los generadores incluidos. El detalle está en [procedencia del audio](assets/audio/PROCEDENCIA.md). Las ilustraciones generadas con ImageGen se documentan en [procedencia visual](assets/PROCEDENCIA.md) y en los archivos de prompts de la carpeta assets. No se incluyeron las capturas usadas como referencia visual.

ChatGPT se utilizó para apoyar la ideación, el código, las revisiones, la documentación y la preparación de la entrega. ImageGen se utilizó para crear las ilustraciones del juego. La [declaración de uso de IA](USO-IA.md) detalla las herramientas, las consignas de revisión, los prompts visuales y las referencias.

En el menú, deslizá de derecha a izquierda para avanzar una carta. Al volver la mano a la derecha, el carrusel queda listo para el siguiente barrido. Las flechas permiten navegar en ambos sentidos.

## Organización

| Archivo | Función |
| --- | --- |
| `ajustes.py` | Dimensiones, paleta y parámetros compartidos. |
| `ambiente.py` | Fondos y animaciones del bosque. |
| `arte_sellos.py` | Arte y cursor de Sellos de luna. |
| `banquete.py` | Reglas y dibujo de Banquete del familiar. |
| `bolsa.py` | Dibujo de la bolsa del primer juego. |
| `cartas.py` | Carrusel de selección y colección. |
| `companero.py` | Compañero animado y guía visual de gestos. |
| `crear_audio.py` | Generador local de música y efectos base. |
| `crear_audio_magico.py` | Generador local de variaciones sonoras. |
| `diario.py` | Recuerdos y persistencia local del progreso. |
| `efectos.py` | Animaciones que acompañan eventos de la partida. |
| `faroles.py` | Secuencias, reglas y dibujo de Faroles del jardín. |
| `gestos.py` | Ilustración del gesto de pinza. |
| `identidad.py` | Nombre, fuentes y recursos visuales. |
| `interfaz.py` | Paneles, botones y tratamiento tipográfico. |
| `juego.py` | Reglas de Bichos a la boca. |
| `main.py` | Eventos, actualización, reloj, pantallas y dibujo en Pygame. |
| `navegacion.py` | Control de regreso al menú. |
| `objetos_anime.py` | Sprites de objetos. |
| `particulas.py` | Emisión y actualización de partículas. |
| `personajes.py` | Dibujo de criaturas. |
| `sellos.py` | Reglas y seguimiento del trazo en Sellos de luna. |
| `sonido.py` | Reproducción y mezcla de música y efectos WAV. |
| `tutorial_animado.py` | Demostraciones visuales de los controles. |
| `vision.py` | Apertura, captura espejada y detección de mano con OpenCV y MediaPipe. |

## Estado

La propuesta requiere probar en vivo comodidad del gesto, alcance del nido y
dificultad. La letra oficial del Obligatorio 2 sigue pendiente de revisar.
Se reutilizan las bibliotecas del curso.

## Pantalla y zona segura

F11 alterna pantalla completa y ventana. La ventana también se puede agrandar;
la imagen conserva sus proporciones y el mouse respeta las bandas laterales.
El nido y los bichos quedan dentro del marco de seguridad. El 64% central
de la cámara controla toda la pantalla: no hace falta llevar los dedos al
borde de la imagen. Si la mano desaparece, se conserva la carga y se detiene
el tiempo hasta recuperarla.

La primera dirección visual usa un jardín nocturno violeta, flores rosas, luna
y criaturas originales con ojos y orejas inspirados en anime. Las referencias
son una guía visual; no se incorporaron las capturas como recursos del juego.

C muestra u oculta una vista espejo con un marco rosa. Mantené el punto
de los dedos dentro de ese marco para recorrer el juego cómodamente.
La madriguera se ilumina al transportar una presa y muestra +1 al entregarla.

## Reacciones y entregas

Al atrapar un violeta aparece un rayo, ojos en cruz y un temblor breve;
la penalización sigue siendo cuatro segundos por captura.
Cada entrega anima un bichito hacia la bolsa y lo conserva visible adentro.
La octava entrega termina su caída antes de mostrar el resultado.
La pausa y la pérdida de mano conservan las animaciones sin descontar tiempo.
El fondo ilustrado original está en assets/jardin-anime-v1.png; su prompt
y procedencia están guardados en assets/PROCEDENCIA.md.

## Personajes ilustrados

El familiar oscuro de ojos rosas responde a la pinza abriendo la boca.
Los amarillos son polillas luminosas y los violetas tienen alas y cuernos
puntiagudos. Ambos se animan suavemente al moverse.
Las tres imágenes transparentes están en assets, junto con sus prompts
en PERSONAJES-PROMPTS.md. personajes.py las carga una sola vez y conserva
las variantes de animación para evitar recalcularlas en cada fotograma.
Las versiones anteriores de dibujo están conservadas en versiones.

## Música y efectos

M silencia o reactiva toda la música y los efectos. La música de fantasía
suena en bucle y baja durante las pausas y picaduras. Hay efectos propios
para elegir, empezar, atrapar, entregar, picadura, escape y resultado.
Los WAV originales están en assets/audio. sonido.py conecta los eventos
del juego con el mezclador de Pygame. crear_audio.py permite regenerarlos
con NumPy; no hace falta ejecutarlo para jugar.


## Minijuego 2: Faroles del jardín

Desde el menú elegí la segunda tarjeta con pinza o clic, o pulsá 2.
Enter inicia desde sus instrucciones y permite repetir al terminar.

1. Mirá la secuencia de faroles que se iluminan. No hay que tocarlos todavía.
2. Cuando diga TU TURNO, acercá la estrella al primer farol y cerrá la pinza.
3. Abrí los dedos, movete al siguiente y cerrá otra vez, respetando el orden.
4. Completá cuatro constelaciones: secuencias de 3, 4, 5 y 6 faroles.

Tenés 75 segundos acumulados de turno. Mirar la secuencia no descuenta tiempo.
Una pinza incorrecta dentro de un farol resta 4 segundos y repite la secuencia.
Hacer pinza fuera de los faroles no penaliza. Sostener la pinza no repite toques.
P pausa. Al perder la mano se congelan tanto el tiempo como la demostración.
M controla el sonido, C la guía de cámara y F11 la pantalla completa.
Esc vuelve al menú y permite alternar con Bichos a la boca.

### Cómo está hecho

faroles.py conserva la secuencia, el paso esperado y las fases mirar, repetir
y celebrar. MediaPipe envía la posición y el instante en que cerrás la pinza.
Solo se registra un toque cuando la estrella está cerca de un farol.
Cada acierto conecta los faroles con una línea; al completar la ronda,
se genera la siguiente secuencia. Las reglas emiten eventos para los sonidos.

Estado: comprobaciones automáticas de rondas, error, fin de tiempo, pausa,
menú y regreso al juego 1 completadas. La comodidad con cámara queda pendiente
de la prueba de Vicky.

## Minijuego 3: Banquete del familiar

Elegí la tercera tarjeta con pinza o clic, o pulsá 3. Enter inicia.
Después de la cuenta 3, 2, 1, mové la mano a izquierda y derecha.
La altura de la canasta permanece fija: no necesitás mover la mano hacia
los bordes ni hacer pinza para atrapar.

- Dulces: suman puntos; a partir de cinco seguidos, cada dulce vale dos.
  A partir de diez, vale tres. Perder un dulce corta el combo.
- Pociones: restan cuatro segundos y cortan el combo.
- Bombas de humo: restan seis segundos y cortan el combo.
- Estrellas: activan un imán durante seis segundos. Atrae solo dulces
  cercanos, no los peligros.
- Meta inicial: 40 puntos de dulzura en 60 segundos.

banquete.py contiene las reglas y el dibujo de los objetos. Actualiza la
posición de caída y comprueba si el objeto cruza la boca de la canasta;
por eso detecta la captura incluso si cruza esa altura entre fotogramas.

La cocina usa el fondo original assets/cocina-anime-v1.png, con prompt en
assets/COCINA-PROMPT.md. Los objetos se dibujan a doble resolución y se
reducen para suavizar los bordes. Son una primera versión para probar.

## Fondos animados

Los tres juegos y el menú tienen movimiento ambiental: vaivén muy suave
del escenario, pétalos y luciérnagas con brillo cambiante. ambiente.py dibuja
estos elementos aparte de las reglas y conserva las variantes del fondo.
La pausa y la pérdida de mano detienen también el ambiente.

Estado del juego 3: pruebas de combos, peligros, atracción selectiva del imán,
victoria, fin de tiempo, pausa, menú y regreso a los anteriores completadas.
Pendiente: comodidad y dificultad con la cámara real.

## Minijuego 4: Sellos de luna

Elegí la cuarta tarjeta o pulsá 4. Enter inicia. Acercate al punto rosa,
cerrá la pinza y seguí el recorrido guiado. El punto avanza a medida que
pasás por los puntos del símbolo, en orden. Podés abrir la pinza y continuar;
el dibujo queda visible. R borra el sello actual sin reiniciar el reloj.

La meta es liberar cuatro espíritus en 90 segundos, dibujando un círculo,
un triángulo, un corazón y una estrella. Al completar cada sello, el espíritu
sale del círculo y comienza el siguiente. La pausa y la pérdida de mano
conservan el avance y detienen el tiempo. P, M, C, F11 y Esc siguen disponibles.

sellos.py verifica el recorrido mediante puntos consecutivos y una tolerancia
de proximidad. No reconoce cualquier dibujo libre: compara el avance con
la guía visible. De este modo se puede aprender el gesto paso a paso.

## Actualización visual de los juegos 2 y 3

Los faroles, dulces, pociones, bombas, estrellas y canasta usan ilustraciones
originales de la misma lámina: assets/objetos-anime-v1.png. El prompt está
en assets/OBJETOS-PROMPT.md y objetos_anime.py carga y conserva los sprites.
Los faroles apagados se oscurecen; al activarse conservan el halo animado.
Las versiones anteriores del dibujo están guardadas en versiones.

Estado: se comprobaron los cuatro sellos, levantar y continuar, borrar,
fin de tiempo y navegación del menú. También se verificaron las reglas de
Faroles y Banquete con sus ilustraciones nuevas. Pendiente la prueba real
con cámara del juego 4 y la valoración visual de Vicky.

## Sellos: inicio limpio e ilustraciones

Cada símbolo espera a que cierres la pinza sobre su primer punto (la joya).
Hasta entonces no guarda ni dibuja trazos, aunque muevas la mano cerrada.
R y cada nuevo símbolo vuelven a activar esa espera. Una vez iniciado,
podés abrir la pinza y continuar sin perder el recorrido.
El marco lunar, espíritu gatito, pluma y joya son ilustraciones originales
de assets/sellos-anime-v1.png; prompt en assets/SELLOS-PROMPT.md.
Se comprobaron el bloqueo previo, el inicio, el borrado y los cuatro sellos.


## Pulido de experiencia y magia

El juego 4 suaviza la posición de la pluma con un filtro temporal y una zona
muerta de 2,5 píxeles para reducir temblores. Cursor y línea comparten esa
posición; el inicio sigue bloqueado hasta llegar a la primera joya.
La estela tiene un núcleo claro, borde rosa y polvo de estrellas que se apaga.
El progreso del sello también se muestra como barra.

Los cuatro juegos emiten partículas y ondas ante capturas y logros. Las
bombas del Banquete producen humo y un golpe grave, el veneno tiene reacción
propia, y los combos e imán muestran avisos y destellos dorados. Las partículas
se detienen al pausar y tienen límites de cantidad y duración.

El cuarto usa sonidos originales de cristal para inicio, avance, sello y
resultado. crear_audio_magico.py permite regenerar esos WAV. M silencia todo.
En menús e instrucciones el cursor es pequeño para no tapar el texto; el
estado de audio queda visible en partida y el tiempo bajo se destaca en rosa.

Se comprobaron el filtro con temblores pequeños, los cuatro sellos con
movimiento a 30 fps, los eventos de sonido y la caducidad de partículas.
Pendiente: ajustar la sensación del filtro y los volúmenes con Vicky.

## Inicio con cartas de colección

Las cuatro portadas son cartas verticales ilustradas. Al pasar el mouse o
la mano giran en unos 0,46 segundos, muestran sus instrucciones y vuelven
al frente al salir. Hacé clic o cerrá la pinza sobre una carta para elegir.
También siguen disponibles las teclas 1 a 4 y la pantalla completa con F11.
El área de selección permanece estable durante el giro para evitar saltos.

Tras la corrección visual de Vicky, el inicio toma una dirección de bosque
pintado a mano: luz cálida, plantas, papel, madera y pequeñas criaturas.
Las imágenes usadas son assets/cartas-bosque-v2.png y
assets/inicio-bosque-v2.png. Los prompts se guardaron en
assets/CARTAS-PROMPTS.md. cartas.py compone títulos y reversos, y anima el giro.
Las versiones góticas anteriores se conservan como archivos aparte.

Se probaron los cuatro destinos, el giro y su reversa, el estado intermedio,
la interacción de mouse/mano y la navegación hacia los juegos. Pendiente:
valoración de la dirección visual nueva y prueba del giro con cámara.

## Nombre, lettering y formato 16:9

La identidad del juego ahora es La casita de los hechizos. El logotipo usa
letras dibujadas especialmente para ese nombre, con casita, hojas y pequeñas
luciérnagas. Está en assets/logo-casita-v1.png; el prompt y la distinción entre
lettering y fuente completa están en assets/LOGO-PROMPT.md.
Los títulos usan Constantia y los textos de lectura Segoe UI del sistema,
con respaldo de Pygame.
No se distribuye una fuente nueva ni los archivos tipográficos de Windows.

La ventana usa un lienzo 1280 x 720 (16:9). El inicio aprovecha todo el ancho
para repartir las cuatro cartas. En partida el fondo y las barras ocupan el
ancho completo y la acción conserva su área segura central de 960 píxeles.
Mouse y cámara respetan esa diferencia; al redimensionar se preserva la
proporción, y F11 alterna con la pantalla completa sin bordes.

Se verificaron la navegación, el clic en una carta con ventana 1600 x 900,
el cambio de pantalla y el retorno a los juegos anteriores. Pendiente la
valoración del nombre, lettering y formato por Vicky.

## Bolsa ilustrada del primer juego

La bolsa usa lino claro, interior verde salvia, lazo rosa y hojas bordadas.
Su ilustración original está en assets/bolsa-bosque-v1.png y el prompt en
assets/BOLSA-PROMPT.md. bolsa.py pinta el fondo y el labio delantero;
efectos.py mantiene las caídas y los ocho bichitos visibles dentro.
Se verificaron las entregas de 1 a 8 y la animación final.

## Texto y paneles de juego

interfaz.py reúne las placas de papel claro, tinta verde y detalles de hojas.
Los cuatro juegos comparten título, progreso y reloj separados; las instrucciones
tienen fondos sólidos y los atajos se presentan como teclas. Segoe UI regular y
negrita evitan las variantes finas que dificultaban leer el texto secundario.
Los botones ajustan su tamaño de letra al ancho disponible, sin deformarla.
Se comprobaron capturas de los cuatro juegos, inicio e instrucciones y la
navegación con pausa y regreso al menú. La prueba de lectura con cámara queda
para la usuaria. Las versiones anteriores están conservadas en versiones/.

## Mundo del bosque, compañero y diario

Los cuatro fondos de mundos-bosque-v3.png forman un mismo mundo pintado:
jardín de día, patio de faroles al atardecer, cocina de la casita y claro de luna.
Ambiente conserva el movimiento y las hojas/luciérnagas animadas. Los objetos
de los juegos 2, 3 y 4 usan los nuevos atlas objetos-bosque-v2.png y
sellos-bosque-v2.png; los prompts están en assets/MUNDO-BOSQUE-PROMPTS.md.

companero.py escucha los eventos del juego: captura, entrega, picadura, escape,
magia y explosión. El familiar se inclina hacia los bichitos, salta al festejar
y se sorprende ante los peligros. Acompaña desde el margen derecho en 2, 3 y 4.
La guía izquierda muestra pinza, carga y pérdida de mano. mano.py avisa cuando
algún punto de la mano entra en el 8% exterior de la cámara. La detección real
de ese aviso debe ajustarse con pruebas de cámara, no con capturas estáticas.

diario.py guarda automáticamente cada partida terminada en datos/diario.json:
partidas, victorias y mejor marca por juego. Una victoria desbloquea un sello;
los cuatro recuerdos forman la colección. D o el botón Mi diario abren el álbum.
El resultado permite repetir con Enter o elegir aventura con Esc/clic/pinza.
El guardado usa un temporal y reemplazo atómico; si el archivo no se puede leer,
no se sobrescribe y se muestra un aviso. datos/ queda excluido de Git.
CASITA_DATOS permite usar otra ruta para pruebas sin tocar la colección real.

Verificación: navegación de los cuatro juegos, resultados y diario; guardado,
recarga, victorias sin duplicados y protección de un archivo corrupto; reglas
de faroles, banquete y sellos; clic escalado a 1600x900 y alternancia F11.
Pruebas en tmp/probar_diario_bosque.py y los scripts de cada minijuego.
Copias previas a esta actualización: versiones/antes-diario-bosque/.


## Explicaciones animadas

tutorial_animado.py dibuja doce demostraciones en bucle con los sprites reales.
En el primer juego se muestran boca y pinza, captura de la polilla y entrega
en la bolsa. Los demás muestran secuencias de faroles, canasta y peligros,
y el inicio y trazado del sello. Las animaciones no alteran partidas ni audio.
Se verificaron cuatro momentos de cada paso y la navegación de instrucciones.

## Inicio con carrusel y mano completa

Carrusel presenta una sola carta, transición lateral, flechas y selección central.
La mano abierta cambia de aventura con un barrido de palma; la pinza selecciona.
ControlMano conserva los 21 puntos xyz de MediaPipe, calcula el centro suavizado
de la palma y distingue dedos extendidos. La vista C dibuja todas las conexiones
y articulaciones. Al perder detección se desactiva la navegación por gestos.
Flechas del teclado o clic lateral cambian de carta; Enter abre la carta actual.
Se verificaron barridos en ambas direcciones, bloqueo de repeticiones, vuelta
circular, selección y navegación al juego. Pendiente prueba real de gestos.

## Colección de recuerdos animados

El diario reúne Mariposa de miel, Farol del crepúsculo, Dulce de la casita
y Espíritu de luna. Los objetos conseguidos flotan con destellos y contorno
de pegatina; al acercar mouse/mano la tarjeta gira para revelar su historia
y récord. Los pendientes muestran silueta misteriosa. Ganar revela el recuerdo
con una aparición animada. El formato de guardado anterior sigue siendo válido.
La mano usa las dos posturas ilustradas de assets/mano-pinza-v2.png, con
procedencia en assets/MANO-PINZA-PROMPT.md. Pruebas: persistencia y giro reversible.

## Revisión de seguimiento por etapas

Inicio y canasta siguen el centro de la palma. Instrucciones, botones, faroles,
bichitos y pluma siguen el índice; la pinza solo genera la acción. Se conserva
el margen seguro de cámara 24%..76%. El reflejo del inicio y de las partidas
usa esa misma transformación para coincidir con el cursor. El inicio muestra
la cámara tenue sobre el área de cartas. El filtro de posición usa tiempo real
y respuesta adaptativa; cambiar referencia o resolución reinicia su posición.
Se comprobó que mover el pulgar no desplaza el cursor del índice, el paso entre
palma/índice y anchos 960/1280, y navegación con cámara simulada por las cuatro
partidas. La calidad de detección real se evalúa con la cámara de la usuaria.

## Corrección de alineación sin zoom (16 de noviembre)

La cámara y el cursor ahora usan el encuadre completo: x normalizado por ancho,
y normalizado por alto. Esto reemplaza el antiguo recorte 24%..76% documentado
arriba: quitarlo de la imagen sin quitarlo del control producía el desfase.
El margen de acción se resuelve en la distribución del juego, sin ampliar la
posición de la mano. tmp/probar_alineacion_camara.py comprueba 18 posiciones
con marcadores en fotogramas sintéticos y su coincidencia con el cursor,
para palma/índice/pinza en 960 y 1280 píxeles de ancho.

## Revisión de fluidez y pinza (16 de noviembre)

entrada_camara.py captura y procesa MediaPipe en un hilo separado. La ventana
consume la muestra más reciente; no se acumula una cola de imágenes antiguas.
El cierre de pinza se entrega una sola vez, con su posición de selección.
Cambiar pantalla invalida muestras de otra resolución o referencia.
Al empezar a pinzar con el índice, el cursor conserva su punto y sigue la
traslación de la palma: plegar dedos no desplaza los botones, pero la mano
puede seguir transportando objetos y dibujando.
interfaz.py reutiliza fuentes y superficies de texto (caché acotada a 512).
La medición de dibujo de Sellos bajó de ~35 a ~7 ms por fotograma. La prueba
con cámara real y ventana activa obtuvo ~33.7 ms entre fotogramas de interfaz
(~30 fps), con MediaPipe ~31.9 ms de mediana. No hubo mano en esa muestra;
la calidad del gesto requiere comprobación de la usuaria.
El carrusel conserva el barrido durante pérdidas de detección menores de
0.35 s y exige detección presente para llenar la selección. Si falla el
índice de cámara predeterminado, se buscan índices 0/1/2 mediante DirectShow.
En esta sesión la cámara funcional fue la 1.
Pruebas: tmp/probar_entrada_camara.py, tmp/probar_alineacion_camara.py,
navegación completa y persistencia del diario.


[Repositorio del Obligatorio 2 en GitHub](https://github.com/vickybev/obligatorio-2-programacion-2).

## Cronología del desarrollo

- **12 de noviembre.** La copia local `antes-diario-bosque` conserva una etapa anterior a la integración del diario. En esa etapa ya se trabajaba con las reglas de Bichos a la boca y los efectos sonoros.
- **13 de noviembre.** La copia local `antes-identidad-interfaz` conserva el diseño anterior al cuaderno botánico. El criterio de tipografía, color y jerarquía de la interfaz quedó documentado en [DISENO-INTERFAZ.md](DISENO-INTERFAZ.md).
- **16 de noviembre.** Se documentaron los ajustes para alinear el cursor con la cámara sin zoom y reducir el salto al cerrar la pinza. Las notas están en las dos revisiones anteriores de este README.
- **20 de noviembre.** El prototipo entró al repositorio común. Luego se concentró la captura en `vision.py` y se quitó el modo de juego con mouse.

Las primeras fechas corresponden a las copias locales y notas del proyecto. El historial de Git comienza con la incorporación al repositorio.

## Niveles de las aventuras

Desde las instrucciones elegí Nivel 1, 2 o 3 con una pinza sobre el botón, con el mouse o con las teclas 1–3. Enter comienza la partida. Al repetir se conserva el nivel.

| Aventura | Nivel 1 | Nivel 2 | Nivel 3 |
| --- | --- | --- | --- |
| Bichos a la boca | 8 en 60 s | 10 en 65 s y más bichos violetas | 13 en 75 s y todavía más violetas |
| Faroles del jardín | 4 secuencias en 75 s | 5 en 80 s, señal más rápida | 6 en 85 s, señal más rápida y más secuencias largas |
| Banquete del familiar | 40 puntos en 60 s | 55 en 65 s, con caída más rápida | 72 en 70 s, con más peligros |
| Sellos de luna | 4 figuras en 90 s | 5 en 105 s, con rombo | 6 en 120 s, con infinito y mayor precisión |

En Sellos de luna, la pluma y el trazo siguen el punto medio del pulgar y el índice. Los tiempos de Faroles corresponden al turno de repetir la secuencia.
