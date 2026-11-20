"""Reglas del primer minijuego, independientes de cámara y dibujo."""
import math
import random

from ajustes import ALTO, ANCHO, NIDO, RADIO_NIDO


def dentro_nido(pos):
    """Usa la misma elipse que aparece dibujada en pantalla."""
    return ((pos[0]-NIDO[0])/85)**2 + ((pos[1]-NIDO[1])/56)**2 <= 1


class Partida:
    def __init__(self):
        self.tiempo = 60.0
        self.puntos = 0
        self.meta = 8
        self.bichos = []
        self.carga = None
        self.mensaje = "Atrapá un bichito con la pinza"
        self.aviso = 3.0
        self.fin = False
        self.eventos = []
        for i in range(11):
            self.crear(i >= 8)

    def crear(self, veneno=False):
        while True:
            x, y = random.uniform(115, 845), random.uniform(175, 555)
            if math.dist((x, y), NIDO) > 135:
                break
        self.bichos.append(dict(x=x, y=y, vx=random.uniform(-45,45),
                                vy=random.uniform(-45,45), malo=veneno,
                                fase=random.random()*math.tau))

    def avisar(self, mensaje):
        self.mensaje, self.aviso = mensaje, 2.5

    def actualizar(self, dt, pos, cerrada, mordida):
        if self.fin or pos is None:
            return
        self.tiempo = max(0, self.tiempo-dt)
        self.aviso = max(0, self.aviso-dt)
        if self.tiempo <= 0:
            self.fin = True
            return
        for b in self.bichos:
            dx, dy = b['x']-pos[0], b['y']-pos[1]
            distancia = math.hypot(dx,dy)
            if distancia < 135 and not cerrada:
                b['vx'] += dx/max(distancia,1)*220*dt
                b['vy'] += dy/max(distancia,1)*220*dt
            b['vx'] += math.sin(b['fase'])*22*dt
            b['vy'] += math.cos(b['fase'])*22*dt
            b['fase'] += dt*2
            velocidad = math.hypot(b['vx'],b['vy'])
            if velocidad > 105:
                b['vx'] *= 105/velocidad
                b['vy'] *= 105/velocidad
            b['x'] += b['vx']*dt
            b['y'] += b['vy']*dt
            if not 105 <= b['x'] <= 855:
                b['vx'] *= -1
                b['x'] = max(105,min(855,b['x']))
            if not 160 <= b['y'] <= 575:
                b['vy'] *= -1
                b['y'] = max(160,min(575,b['y']))
            # El nido permanece libre para que la entrega sea legible.
            if math.dist((b['x'],b['y']), NIDO) < RADIO_NIDO+20:
                b['vx'], b['vy'] = -75, -45

        if self.carga is not None:
            self.carga['resta'] -= dt
            if not cerrada:
                if dentro_nido(pos):
                    self.puntos += 1
                    self.eventos.append(("entrega", tuple(pos), self.puntos))
                    self.avisar(random.choice(["¡ÑAM! Uno para la despensa", "Entrega deliciosa", "¡Otro bichito a casa!"]))
                    self.carga = None
                    self.crear()
                    if self.puntos >= self.meta:
                        self.fin = True
                else:
                    self.soltar(pos, "¡Se escapó! Soltalo dentro del nido")
            elif self.carga['resta'] <= 0:
                self.soltar(pos, "¡Se zafó! Tenés 7 segundos para llevarlo")
            return

        if mordida:
            cerca = [b for b in self.bichos if math.dist(pos,(b['x'],b['y'])) < 53]
            if cerca:
                b = min(cerca,key=lambda b:math.dist(pos,(b['x'],b['y'])))
                self.bichos.remove(b)
                if b['malo']:
                    self.tiempo = max(0,self.tiempo-4)
                    self.eventos.append(('picadura', tuple(pos), 0))
                    self.avisar("¡ACHÍS! El violeta pica. -4 segundos")
                    self.crear(True)
                else:
                    self.carga = dict(b, resta=7.0)
                    self.eventos.append(("captura", tuple(pos), 0))
                    self.avisar("¡Lo tenés! Mantené la pinza y soltá en el nido")

    def soltar(self, pos, mensaje):
        self.eventos.append(("escape", tuple(pos), 0))
        b = self.carga
        b.update(x=max(105,min(855,pos[0])),y=max(160,min(575,pos[1])),vx=-65,vy=-30)
        self.bichos.append(b)
        self.carga = None
        self.avisar(mensaje)
