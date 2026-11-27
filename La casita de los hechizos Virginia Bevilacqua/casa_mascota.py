"""Rincón persistente del compañero de La casita."""
import json
import math
import random
from pathlib import Path
from functools import lru_cache

import pygame

from interfaz import boton, escribir, papel, PAPEL, MUSGO, TINTA
from personajes import dibujar_familiar
from armario import PRENDAS

CUIDADOS = ('Comida', 'Baño', 'Juego', 'Caricias')
HABITACION = pygame.Rect(53, 159, 854, 462)
MASCOTA = pygame.Rect(399, 378, 162, 139)
CENTRO_MASCOTA = (480, 448)
BOCA = (480, 467)
CONTACTO_JUGUETE = (550, 457)
TIEMPO_LANZAMIENTO = .55
TIEMPO_REGRESO = .8
PUERTA = pygame.Rect(641, 364, 137, 73)
TIRADOR = (716, 399)
OBJETOS = {'comida': (166, 477), 'esponja': (835, 477),
           'pelota': (585, 538), 'aro': (676, 533)}


@lru_cache(maxsize=1)
def fondo_habitacion():
    """Carga la ilustración del cuarto una sola vez."""
    ruta = Path(__file__).parent / 'assets' / 'habitacion-familiar.png'
    return pygame.transform.smoothscale(pygame.image.load(str(ruta)).convert(), HABITACION.size)


def dibujar_objeto(s, nombre, pos, giro=0):
    """Dibuja los objetos que se pueden agarrar, con su contorno visible."""
    x, y = map(round, pos)
    if nombre == 'esponja':
        pygame.draw.rect(s, (122, 80, 42), (x-23,y-14,46,28), border_radius=7)
        pygame.draw.rect(s, (248, 192, 88), (x-20,y-12,40,24), border_radius=6)
        for dx, dy in ((-10,-4),(5,4),(11,-5),(-3,7)):
            pygame.draw.circle(s, (211,147,58), (x+dx,y+dy),3)
    elif nombre == 'comida':
        rect = pygame.Rect(x-19,y-11,38,22)
        pygame.draw.rect(s, (112,66,38), rect, border_radius=6)
        pygame.draw.rect(s, (197,132,67), rect.inflate(-4,-4), border_radius=5)
        for dx, dy in ((-10,-3),(0,4),(9,-4),(12,4),(-5,6)):
            pygame.draw.circle(s,(251,203,111),(x+dx,y+dy),2)
    elif nombre == 'pelota':
        pygame.draw.circle(s,(113,53,89),(x,y),17)
        pygame.draw.circle(s,(224,120,153),(x-1,y-2),14)
        pygame.draw.arc(s,(255,218,180),(x-11,y-15,18,23),.2 + giro,2.6 + giro,3)
    else:
        pygame.draw.circle(s,(44,85,84),(x,y),21,7)
        pygame.draw.circle(s,(139,212,186),(x-1,y-1),19,4)
        marca = (round(x + 17 * math.cos(giro)), round(y + 17 * math.sin(giro)))
        pygame.draw.circle(s,(250,222,150),marca,3)


class CasaMascota:
    """Guarda interacciones del compañero sin penalizar el paso del tiempo."""
    def __init__(self, ruta_diario):
        """Recupera los cuidados asociados a este perfil."""
        self.ruta = ruta_diario.with_name('mascota.json')
        try:
            datos = json.loads(self.ruta.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            datos = {}
        self.cuidados = {
            accion: datos[accion] if isinstance(datos, dict) and type(datos.get(accion)) is int
            and datos[accion] >= 0 else 0 for accion in CUIDADOS
        }
        prenda = datos.get('prenda') if isinstance(datos, dict) else None
        self.prenda = tuple(prenda) if isinstance(prenda, list) and len(prenda) == 2 and all(
            type(i) is int for i in prenda) and 0 <= prenda[0] < 4 and 0 <= prenda[1] < 3 else None
        self.armario = False
        self.mensaje = 'Tu compañero está feliz de verte'
        self.accion = None
        self.hasta = 0
        self.objeto = None
        self.pos_objeto = None
        self.ultimo_roce = None
        self.espuma = 0.0
        self.vuelo = None
        self.apertura = 0.0

    def cuidar(self, accion, ahora):
        """Suma el cuidado, responde con una animación y guarda el estado."""
        self.cuidados[accion] += 1
        self.accion = accion
        self.hasta = ahora + 1.8
        self.mensaje = {
            'Comida': random.choice(('¡Ñam, ñam!', '¡Qué rico estaba!', '¡Un bocadito delicioso!')),
            'Baño': '¡Listo! Quedó limpito',
            'Juego': '¡Otra vez! Le encantó jugar',
            'Caricias': 'Cerró los ojos de lo contento que está',
        }[accion]
        self.guardar()

    def guardar(self):
        """Guarda los cuidados y la única prenda que está puesta."""
        temporal = self.ruta.with_suffix('.tmp')
        try:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            temporal.write_text(json.dumps({**self.cuidados, 'prenda': self.prenda}, ensure_ascii=False), encoding='utf-8')
            temporal.replace(self.ruta)
        except OSError:
            self.mensaje = 'El cuidado quedó en esta sesión. No se pudo guardar.'

    def equipar(self, prenda, diario):
        """Equipa una prenda ganada o vuelve al aspecto original."""
        if prenda is not None and prenda[1] >= diario.niveles(prenda[0] + 1):
            return
        self.prenda = prenda
        self.guardar()

    def dibujar_armario(self, pantalla, puntero, activar, ahora, diario):
        """Muestra prendas ganadas, bloqueadas y la que está puesta."""
        papel(pantalla, (53,40,854,600))
        escribir(pantalla,'Armario de tu compañero',(480,95),38,titulo=True)
        dibujar_familiar(pantalla,(188,268),True,ahora,prenda=self.prenda)
        nombre = PRENDAS[self.prenda[0]][self.prenda[1]] if self.prenda is not None else 'Aspecto original'
        escribir(pantalla, nombre, (188,360),19,negrita=True,ancho=190)
        volver = pygame.Rect(82,512,192,46)
        quitar = pygame.Rect(82,455,192,46)
        boton(pantalla,volver,'Volver a la casa')
        boton(pantalla,quitar,'Aspecto original')
        if activar and puntero is not None:
            if volver.collidepoint(puntero):
                self.armario = False
                return
            if quitar.collidepoint(puntero):
                self.equipar(None, diario)
        for grupo, prendas in enumerate(PRENDAS):
            for nivel, nombre_prenda in enumerate(prendas):
                rect = pygame.Rect(294+nivel*190,162+grupo*88,182,73)
                ganada = nivel < diario.niveles(grupo + 1)
                puesta = self.prenda == (grupo, nivel)
                if ganada and activar and puntero is not None and rect.collidepoint(puntero):
                    self.equipar((grupo,nivel), diario)
                    puesta = True
                papel(pantalla, rect, (209,225,191) if puesta else (238,225,194) if ganada else (225,218,197))
                escribir(pantalla,nombre_prenda,(rect.centerx,rect.top+24),17,ancho=164,negrita=ganada)
                estado = 'Puesta' if puesta else 'Equipar' if ganada else f'Premio de nivel {nivel + 1}'
                escribir(pantalla,estado,(rect.centerx,rect.top+50),16,MUSGO)
        escribir(pantalla,'Completá niveles para sumar prendas al armario',(480,590),20)

    def soltar(self):
        """Vuelve a dejar el objeto en su lugar si se cancela el gesto."""
        self.objeto = None
        self.pos_objeto = None
        self.ultimo_roce = None
        self.espuma = 0
        self.apertura = 0

    def actualizar(self, puntero, presiona, sostiene, ahora):
        """Interpreta pinza, arrastre y suelta en las estaciones del cuarto."""
        if puntero is None:
            self.soltar()
            return
        if presiona and self.objeto is None and not self.vuelo:
            if math.dist(puntero, TIRADOR) <= 25:
                self.objeto = 'puerta'
                self.pos_objeto = puntero
            else:
                for nombre, posicion in OBJETOS.items():
                    if math.dist(puntero, posicion) <= 30:
                        self.objeto = nombre
                        self.pos_objeto = puntero
                        break
                if self.objeto is None and MASCOTA.collidepoint(puntero):
                    self.cuidar('Caricias', ahora)
        if self.objeto is None:
            return
        if not sostiene:
            if self.objeto in ('pelota', 'aro'):
                origen = self.pos_objeto
                if math.dist(origen, OBJETOS[self.objeto]) > 26:
                    self.vuelo = (self.objeto, origen, ahora)
            self.soltar()
            return
        if self.objeto == 'puerta':
            self.apertura = max(0, min(1, (self.pos_objeto[0] - puntero[0]) / 54))
            if self.apertura >= 1:
                self.armario = True
                self.soltar()
            return

        self.pos_objeto = puntero
        if self.objeto == 'comida' and math.dist(puntero, BOCA) < 34:
            self.cuidar('Comida', ahora)
            self.soltar()
        elif self.objeto == 'esponja':
            if not MASCOTA.collidepoint(puntero):
                self.ultimo_roce = None
                return
            if self.ultimo_roce is not None:
                distancia = math.dist(puntero, self.ultimo_roce)
                if 3 <= distancia <= 65:
                    self.espuma += distancia
                if distancia < 3:
                    return
            self.ultimo_roce = puntero
            if self.espuma >= 140:
                self.cuidar('Baño', ahora)
                self.soltar()

    def dibujar(self, pantalla, puntero, activar, ahora, diario, sostenido=False):
        """Dibuja la habitación y anima la respuesta a cada cuidado."""
        if self.armario:
            self.dibujar_armario(pantalla,puntero,activar,ahora,diario)
            return
        self.actualizar(puntero,activar,sostenido,ahora)
        if self.armario:
            self.dibujar_armario(pantalla,puntero,False,ahora,diario)
            return

        papel(pantalla, (35,40,890,635))
        escribir(pantalla,'La casa de tu compañero',(433,91),37,titulo=True,ancho=650)
        pantalla.blit(fondo_habitacion(),HABITACION)
        pygame.draw.rect(pantalla,(116,91,62),HABITACION,2)

        # El pomo y la hoja móvil siguen el frente del mueble pintado en el fondo.
        ancho = round(PUERTA.width * (1 - self.apertura * .8))
        puerta = pygame.Rect(PUERTA.left,PUERTA.top,ancho,PUERTA.height)
        pygame.draw.rect(pantalla,(86,49,28),PUERTA,border_radius=3)
        pygame.draw.rect(pantalla,(145,86,44),puerta,border_radius=3)
        if ancho > 24:
            pygame.draw.rect(pantalla,(181,119,66),puerta.inflate(-14,-13),2,border_radius=3)
        pomo = (min(puerta.right - 8,TIRADOR[0]),TIRADOR[1])
        if puntero is not None and math.dist(puntero, TIRADOR) <= 25:
            pygame.draw.circle(pantalla,(255,223,149),pomo,12,2)
        pygame.draw.circle(pantalla,(245,199,102),pomo,7)
        escribir(pantalla,'Armario',(712,350),19,PAPEL,negrita=True)

        # Estaciones alrededor de una alfombra, en la zona cómoda de la cámara.
        pygame.draw.ellipse(pantalla,(99,67,44),(121,469,90,27))
        pygame.draw.ellipse(pantalla,(190,150,85),(124,466,84,25),3)
        pygame.draw.rect(pantalla,(91,131,126),(800,473,70,30),border_radius=9)
        pygame.draw.ellipse(pantalla,(174,217,208),(798,466,74,18))
        for i in range(5):
            pygame.draw.circle(pantalla,(222,245,232),(808 + i*12,472 - i%2*6),9)

        salto = 0
        if self.vuelo:
            juguete, origen, inicio = self.vuelo
            tiempo = ahora - inicio
            salto = 36 * math.sin(math.pi * min(1, tiempo / 1.1))
            if tiempo >= TIEMPO_LANZAMIENTO + TIEMPO_REGRESO:
                self.vuelo = None
                self.cuidar('Juego', ahora)
        activo = ahora < self.hasta
        boca_abierta = self.objeto == 'comida' and self.pos_objeto is not None and math.dist(self.pos_objeto, BOCA) < 100
        if activo and self.accion == 'Comida':
            tiempo_comiendo = 1.8 - (self.hasta - ahora)
            boca_abierta = tiempo_comiendo < .8 and int(tiempo_comiendo * 9) % 2 == 0
        if self.vuelo:
            boca_abierta = False
        mascota = (CENTRO_MASCOTA[0], CENTRO_MASCOTA[1] - salto)
        pygame.draw.ellipse(pantalla,(91,81,49),(414,512,132,18))
        dibujar_familiar(pantalla,mascota,not boca_abierta,ahora,prenda=self.prenda,escala=1.62)
        if self.vuelo:
            regreso = max(0, (tiempo - TIEMPO_LANZAMIENTO) / TIEMPO_REGRESO)
            if regreso:
                destino = OBJETOS[juguete]
                avance = 1 - (1 - regreso) ** 2
                x, y = pygame.Vector2(CONTACTO_JUGUETE).lerp(destino, avance)
                y -= 37 * math.sin(math.pi * regreso)
            else:
                avance = tiempo / TIEMPO_LANZAMIENTO
                x, y = pygame.Vector2(origen).lerp(CONTACTO_JUGUETE, avance)
                y -= 60 * math.sin(math.pi * avance)
            dibujar_objeto(pantalla,juguete,(x,y),tiempo * 11 % math.tau)
            if abs(tiempo - TIEMPO_LANZAMIENTO) < .09:
                cx, cy = CONTACTO_JUGUETE
                for dx, dy in ((1, -1), (1, 0), (1, 1)):
                    pygame.draw.line(pantalla,(255,226,130),
                                     (cx + dx*22, cy + dy*18), (cx + dx*31, cy + dy*27),2)

        for objeto, posicion in OBJETOS.items():
            volando = self.vuelo and objeto == self.vuelo[0]
            if self.objeto != objeto and not volando:
                dibujar_objeto(pantalla,objeto,posicion)
        if self.objeto in OBJETOS:
            dibujar_objeto(pantalla,self.objeto,self.pos_objeto)

        if self.espuma or (activo and self.accion == 'Baño'):
            cantidad = min(12, int(self.espuma//12)+2) if self.espuma else 8
            for i in range(cantidad):
                a = i * 2.4
                x, y = round(480+math.cos(a)*(22+i*3)), round(448+math.sin(a)*(18+i*2))
                if self.espuma:
                    pygame.draw.circle(pantalla,(218,246,237),(x,y),8+i%4)
                    pygame.draw.circle(pantalla,(123,183,183),(x,y),8+i%4,2)
                else:
                    pygame.draw.line(pantalla,(255,226,130),(x-5,y),(x+5,y),2)
                    pygame.draw.line(pantalla,(255,226,130),(x,y-5),(x,y+5),2)
        mensaje = self.mensaje if activo else {
            'comida':'Acercá el bocadito a su boca',
            'esponja':'Pasá la esponja varias veces sobre el pelo',
            'pelota':'Arrastrá la pelota y soltala',
            'aro':'Arrastrá el aro y soltalo',
            'puerta':'Llevá el tirador hacia la izquierda',
        }.get(self.objeto,'Hacé pinza para agarrar un objeto o acariciar al compañero')
        if self.objeto is None and puntero is not None and math.dist(puntero, TIRADOR) <= 25:
            mensaje = 'Hacé pinza en el tirador y arrastrá hacia la izquierda'
        escribir(pantalla,mensaje,(480,646),21,ancho=800)
        for nombre, x in (('Bocadito',166),('Pelota',585),('Aro',676),('Esponja',835)):
            papel(pantalla,(x-44,564 if nombre in ('Pelota','Aro') else 509,88,25))
            escribir(pantalla,nombre,(x,576 if nombre in ('Pelota','Aro') else 521),16)
