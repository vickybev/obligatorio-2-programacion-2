# Cuaderno botánico de la casita

La interfaz comparte papel crema con fibras discretas, tinta verde bosque,
costuras de lino, señaladores y separadores de hojas. Las páginas grandes
muestran encuadernación lateral; las acciones principales usan cintas textiles.

Gabriola se reserva para títulos, cifras destacadas y acciones principales.
Candara regular y negrita resuelven instrucciones, estados y controles.
Se usan las fuentes instaladas de Windows, sin redistribuir sus archivos.
Los textos se ajustan por tamaño, conservando sus proporciones.

Escala nominal: portada de aventura 48, título de página 32–39,
título de partida 32, acción 27, indicación 26, cuerpo 18–22,
etiqueta 16–17. Las instrucciones tienen tres columnas ilustradas;
el marcador de partida reúne capítulo, objetivo y reloj en una sola franja.

Papel #F7EED3 y tinta #27402E ofrecen contraste alto en las zonas de lectura.
El diseño está implementado en interfaz.py y aplicado al inicio, cartas,
instrucciones, partidas, pausas, cuenta regresiva, resultados y diario.
Versiones previas: versiones/antes-identidad-interfaz/.

DesignSignalPacket.typography_state:
- font_families: Gabriola (display), Candara (body)
- scale_ratios: headline/body 2.4, section/body 1.6
- text_zones: instructions [42,40,876,604], HUD [16,6,928,86], footer [16,625,928,93]
- exact_copy_locks: nombres de las cuatro aventuras y La casita de los hechizos

QA: capturas del inicio, instrucciones, HUD, resultado y álbum; navegación
y pruebas de persistencia del diario. La aprobación visual depende de Vicky.
