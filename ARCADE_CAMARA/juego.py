"""Reglas del primer minijuego, independientes de cámara y dibujo."""
import math
import random

from ajustes import ALTO, ANCHO, NIDO, RADIO_NIDO, NIVELES_BICHOS, LUCIERNAGA_DURACION


REFUGIO_LUNA = (254, 476)

def dentro_nido(pos, centro=NIDO):
    """Usa la misma elipse que aparece dibujada en pantalla."""
    return ((pos[0]-centro[0])/85)**2 + ((pos[1]-centro[1])/56)**2 <= 1


class Partida:
    """Controla la captura y la entrega de bichos antes de que se acabe el tiempo."""
    def __init__(self, nivel=0):
        """Prepara el reloj, la meta y la población inicial de bichos."""
        self.tiempo, self.meta = NIVELES_BICHOS[nivel]
        self.puntos = 0
        self.nivel = nivel
        self.pos_anterior = None
        self.tipo_siguiente = 0
        self.bonus = None
        self.bonus_en = 5.0
        self.luz = 0.0
        self.bichos = []
        self.carga = None
        self.mensaje = "Atrapá un bichito con la pinza"
        self.aviso = 3.0
        self.fin = False
        self.eventos = []
        for i in range(11 + nivel * 2):
            self.crear(i >= 8)

    def crear(self, veneno=False):
        """Crea un bicho con una posición y un movimiento propios."""
        while True:
            x, y = random.uniform(115, 845), random.uniform(175, 555)
            if math.dist((x, y), NIDO) > 135:
                break
        refugio = self.nivel == 2 and not veneno and self.tipo_siguiente % 2 == 1
        if not veneno:
            self.tipo_siguiente += 1
        self.bichos.append(dict(x=x, y=y, vx=random.uniform(-45,45),
                                vy=random.uniform(-45,45), malo=veneno,
                                fase=random.random()*math.tau, luna=refugio))

    def avisar(self, mensaje):
        """Muestra un mensaje breve sobre lo que pasó en la partida."""
        self.mensaje, self.aviso = mensaje, 2.5

    def refugio(self):
        """Devuelve el destino de la criatura que llevás en la pinza."""
        return REFUGIO_LUNA if self.carga and self.carga.get('luna') else NIDO

    def actualizar(self, dt, pos, cerrada, mordida):
        """Avanza los bichos y aplica la pinza, la entrega y las penalizaciones."""
        if self.fin or pos is None:
            self.pos_anterior = None
            return
        rapidez = math.dist(pos, self.pos_anterior) / max(dt, .001) if self.pos_anterior else 0
        self.pos_anterior = tuple(pos)
        self.tiempo = max(0, self.tiempo-dt)
        self.aviso = max(0, self.aviso-dt)
        if self.nivel:
            self.luz = max(0, self.luz - dt)
            if self.bonus is None and not self.luz:
                self.bonus_en -= dt
                if self.bonus_en <= 0:
                    self.bonus = (random.randint(350, 610), random.randint(210, 270))
        if self.tiempo <= 0:
            self.fin = True
            return
        for b in self.bichos:
            dx, dy = b['x']-pos[0], b['y']-pos[1]
            distancia = math.hypot(dx,dy)
            if distancia < 135 and not cerrada:
                b['vx'] += dx/max(distancia,1)*220*dt
                b['vy'] += dy/max(distancia,1)*220*dt
            if self.nivel == 1 and not self.luz and not b['malo'] and rapidez > 520 and distancia < 105:
                b['asustado'] = .45
                b['vx'] += dx / max(distancia, 1) * 95
                b['vy'] += dy / max(distancia, 1) * 95
            b['asustado'] = max(0, b.get('asustado', 0) - dt)
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
                if dentro_nido(pos, self.refugio()):
                    self.puntos += 1
                    self.eventos.append(("entrega", tuple(pos), self.puntos))
                    self.avisar(random.choice(["¡ÑAM! Uno para la despensa", "Entrega deliciosa", "¡Otro bichito a casa!"]))
                    self.carga = None
                    self.crear()
                    if self.puntos >= self.meta:
                        self.fin = True
                else:
                    mensaje = "Buscá la bolsa con la marca de ese bicho" if self.nivel == 2 else "¡Se escapó! Soltalo dentro del nido"
                    self.soltar(pos, mensaje)
            elif self.carga['resta'] <= 0:
                self.soltar(pos, "¡Se zafó! Tenés 7 segundos para llevarlo")
            return

        if mordida:
            if self.bonus and math.dist(pos, self.bonus) < 62:
                self.bonus = None
                self.bonus_en = 12.0
                self.luz = LUCIERNAGA_DURACION
                self.avisar('¡Luz de encanto! Más alcance para atrapar bichitos')
                self.eventos.append(('captura', tuple(pos), 0))
                return
            alcance = 82 if self.luz else 53
            cerca = [b for b in self.bichos if math.dist(pos,(b['x'],b['y'])) < alcance
                     and (self.luz or not b.get('asustado'))]
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
                    if self.nivel == 2:
                        destino = 'Luna' if self.carga.get('luna') else 'Sol'
                        self.avisar(f'Mantené la pinza y soltá en la bolsa {destino}')
                    else:
                        self.avisar("¡Lo tenés! Mantené la pinza y soltá en el nido")
            elif self.nivel == 1 and any(b.get('asustado') and math.dist(pos, (b['x'], b['y'])) < 105 for b in self.bichos):
                self.avisar("¡Se asustó! Acercate despacio")

    def soltar(self, pos, mensaje):
        """Deja libre el bicho cargado en la posición indicada."""
        self.eventos.append(("escape", tuple(pos), 0))
        b = self.carga
        b.update(x=max(105,min(855,pos[0])),y=max(160,min(575,pos[1])),vx=-65,vy=-30)
        self.bichos.append(b)
        self.carga = None
        self.avisar(mensaje)
