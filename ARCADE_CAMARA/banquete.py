"""Minijuego 3: canasta por cámara, dulces, peligros, combos e imán."""
import math
import random
from functools import lru_cache
from pathlib import Path
import pygame
from objetos_anime import sprite
from interfaz import cabecera, pie, papel, escribir

ROSA=(233,192,111)
CREMA=(247,239,210)
TINTA=(30,19,41)
ALTURA_CANASTA=555
DULCES = ("Miel", "Frutilla", "Menta")
COLORES_DULCES = ((249,214,127),(248,165,176),(185,232,188))


from ajustes import NIVELES_BANQUETE


class Banquete:
    """Controla la canasta, los objetos que caen y el combo de dulces."""
    def __init__(self, nivel=0):
        """Prepara la canasta, el reloj y la lista de objetos."""
        self.tiempo, self.meta = NIVELES_BANQUETE[nivel]
        self.tiempo_inicial = self.tiempo
        self.nivel = nivel
        self.puntos=0
        self.fin=False
        self.eventos=[]
        self.objetos=[]
        self.particulas=[]
        self.x=480
        self.y=440
        self.y_anterior=440
        self.combo=0
        self.mejor_combo=0
        self.iman=0.0
        self.golpe=0.0
        self.cuenta=3.0
        self.hasta_objeto=.3
        self.hasta_estrella=8.0
        self.mensaje='¡Prepará la canasta!'
        self.aviso=2.0
        self.recogidos=0
        self.pedido = [0] if nivel == 1 else [0, 1, 2] if nivel == 2 else []
        self.paso_pedido = 0

    @property
    def multiplicador(self):
        """Devuelve el valor de un dulce según el combo acumulado."""
        return min(3,1+self.combo//5)

    def crear(self,tipo=None):
        """Incorpora un objeto que cae desde arriba de la pantalla."""
        if tipo is None:
            tipo=random.choices(['dulce','pocion','bomba'],((76,16,8), (72,17,11), (68,18,14))[self.nivel])[0]
        self.objetos.append(dict(tipo=tipo,x=random.uniform(125,835),y=120.,
                                 velocidad=random.uniform(130,175)+self.nivel*24+(self.tiempo_inicial-self.tiempo)*.9,
                                 fase=random.random()*math.tau,variante=random.randrange(3)))

    def avisar(self,mensaje):
        """Guarda un mensaje breve para mostrar durante la ronda."""
        self.mensaje=mensaje
        self.aviso=1.8

    def recoger(self,objeto):
        """Aplica el efecto del objeto que cruzó la boca de la canasta."""
        tipo=objeto['tipo']
        if tipo=='dulce':
            self.combo+=1
            self.mejor_combo=max(self.mejor_combo,self.combo)
            valor=self.multiplicador
            completo = False
            if self.pedido and objeto.get('variante') == self.pedido[self.paso_pedido]:
                self.paso_pedido += 1
                completo = self.paso_pedido == len(self.pedido)
                valor += 4 if self.nivel == 1 else 7 if completo else 0
                if completo:
                    self.paso_pedido = 0
                    self.pedido = [(tipo + 1) % len(DULCES) for tipo in self.pedido]
            self.puntos+=valor
            if self.combo in (5,10):
                self.eventos.append(("combo",(self.x,self.y),valor))
            self.recogidos+=1
            self.eventos.append(('captura',(self.x,self.y),0))
            self.avisar(f'+{valor}  ¡Pedido completo!' if completo else f'+{valor}  ¡Dulce adentro!')
            self.particulas.append(dict(x=objeto['x'],y=self.y,t=.8,texto=f'+{valor}',malo=False))
            if self.puntos>=self.meta:
                self.fin=True
        elif tipo=='estrella':
            self.iman=6.0
            self.eventos.append(('magia',(self.x,self.y),0))
            self.avisar('¡IMÁN! Los dulces cercanos vienen hacia vos')
        else:
            penalizacion=4 if tipo=='pocion' else 6
            self.tiempo=max(0,self.tiempo-penalizacion)
            self.combo=0
            self.golpe=.7
            self.eventos.append(('veneno' if tipo=='pocion' else 'explosion',(self.x,self.y),0))
            self.avisar(f'¡VENENO! -{penalizacion} s' if tipo=='pocion' else f'¡PUF! -{penalizacion} s')
            self.particulas.append(dict(x=self.x,y=self.y,t=.8,texto=f'-{penalizacion} s',malo=True))
            if self.tiempo<=0:
                self.fin=True

    def actualizar(self,dt,pos,cerrada=False,mordida=False):
        """Mueve los objetos y comprueba el cruce de la canasta entre cuadros."""
        if self.fin or pos is None:
            return
        self.x=max(100,min(860,pos[0]))
        self.y_anterior=self.y
        self.y=max(190,min(550,pos[1]))
        if self.cuenta>0:
            self.cuenta=max(0,self.cuenta-dt)
            return
        self.tiempo=max(0,self.tiempo-dt)
        self.iman=max(0,self.iman-dt)
        self.golpe=max(0,self.golpe-dt)
        self.aviso=max(0,self.aviso-dt)
        for particula in self.particulas:
            particula['t']-=dt
            particula['y']-=dt*38
        self.particulas=[p for p in self.particulas if p['t']>0]
        if self.tiempo<=0:
            self.fin=True
            return
        self.hasta_objeto-=dt
        self.hasta_estrella-=dt
        if self.hasta_objeto<=0:
            self.crear()
            self.hasta_objeto=random.uniform(.65,.95)-min(.18,(self.tiempo_inicial-self.tiempo)*.003)
        if self.hasta_estrella<=0:
            self.crear('estrella')
            self.hasta_estrella=10
        pendientes=[]
        for objeto in self.objetos:
            anterior=objeto['y']
            if self.iman>0 and objeto['tipo']=='dulce' and objeto['y']>220 and abs(objeto['x']-self.x)<195:
                objeto['x']+=(self.x-objeto['x'])*min(1,dt*4)
            objeto['y']+=objeto['velocidad']*dt
            if ((anterior-self.y_anterior)*(objeto['y']-self.y)<=0 or abs(objeto['y']-self.y)<24) and abs(objeto['x']-self.x)<=65:
                self.recoger(objeto)
            elif objeto['y']>610:
                if objeto['tipo']=='dulce':
                    self.combo=0
                    self.avisar('Se escapó un dulce. ¡Armá otro combo!')
            else:
                pendientes.append(objeto)
            if self.fin:
                break
        self.objetos=pendientes

    def dibujar(self,pantalla,fuentes,ahora):
        """Dibuja el marcador, la canasta y los objetos en juego."""
        def texto(contenido,pos,tam=24,color=CREMA):
            """Escribe una línea del marcador con la fuente indicada."""
            imagen=fuentes[tam].render(contenido,True,color)
            pantalla.blit(imagen,imagen.get_rect(center=pos))
        estado=f'COMBO {self.combo} · x{self.multiplicador}'
        if self.iman>0:estado+=f' · IMÁN {math.ceil(self.iman)} s'
        cabecera(pantalla,3,'Banquete del familiar',estado,'DULZURA',self.puntos,self.meta,self.tiempo)
        if self.pedido:
            pedido = ' → '.join(DULCES[i] for i in self.pedido[self.paso_pedido:])
            papel(pantalla, (278, 124, 404, 46))
            escribir(pantalla, f'Pedido: {pedido}', (480, 147), 21, negrita=True)
        for objeto in self.objetos:
            dibujar_objeto(pantalla,objeto,ahora)
            if self.pedido and objeto['tipo'] == 'dulce':
                x, y = round(objeto['x']), round(objeto['y'])
                pygame.draw.circle(pantalla, COLORES_DULCES[objeto['variante']], (x,y-21), 12)
                escribir(pantalla, DULCES[objeto['variante']][0], (x,y-21), 15, TINTA, negrita=True)
        x=self.x+(math.sin(ahora*60)*5 if self.golpe else 0)
        if self.iman>0:
            pygame.draw.arc(pantalla,(244,202,130),(x-150,self.y-135,300,180),0,math.pi,2)
            for j in range(5):
                ang=ahora*2+j*math.pi/5
                pygame.draw.circle(pantalla,(255,218,137),(int(x+math.cos(ang)*96),int(self.y-25-math.sin(ang)*47)),3)
        canasta(pantalla,x,self.y,self.recogidos,self.golpe>0)
        for particula in self.particulas:
            texto(particula['texto'],(particula['x'],particula['y']-38),34,(255,158,192) if particula['malo'] else (255,229,149))
        if self.golpe>0:
            for j in range(6):
                a=ahora*4+j*math.tau/6
                pygame.draw.circle(pantalla,(126,76,143),(int(x+math.cos(a)*65),int(self.y-20+math.sin(a)*30)),9)
        if self.cuenta>0:
            papel(pantalla,(270,227,420,150))
            escribir(pantalla,str(math.ceil(self.cuenta)),(480,280),65,negrita=True)
            escribir(pantalla,'Prepará la canasta',(480,349),24,titulo=True)
        mensaje=self.mensaje if self.aviso>0 else 'Dulces sí. Pociones y bombas no. ¡Buscá la estrella!'
        pie(pantalla,mensaje,'Mové la mano arriba, abajo y a los lados. Sin hacer pinza.')



@lru_cache(maxsize=12)
def icono(tipo,variante=0):
    """Ilustraciones pequeñas a doble resolución para bordes suaves."""
    ilustracion=sprite(tipo,58,58)
    if ilustracion is not None:
        if tipo=='dulce' and variante:
            ilustracion=ilustracion.copy()
            ilustracion.fill((235,215,255,255) if variante==1 else (255,235,200,255),special_flags=pygame.BLEND_RGBA_MULT)
        return ilustracion
    s=pygame.Surface((112,112),pygame.SRCALPHA)
    if tipo=='dulce':
        color=[(248,155,190),(140,212,191),(249,203,125)][variante]
        pygame.draw.polygon(s,TINTA,[(13,30),(40,42),(40,70),(13,82),(21,56)])
        pygame.draw.polygon(s,color,[(17,36),(40,46),(40,66),(17,76),(25,56)])
        pygame.draw.polygon(s,TINTA,[(99,30),(72,42),(72,70),(99,82),(91,56)])
        pygame.draw.polygon(s,color,[(95,36),(72,46),(72,66),(95,76),(87,56)])
        pygame.draw.circle(s,TINTA,(56,56),29)
        pygame.draw.circle(s,color,(56,56),25)
        pygame.draw.arc(s,(255,241,220),(40,40,32,32),0,math.tau,4)
        pygame.draw.arc(s,(255,241,220),(47,47,18,18),0,math.pi*1.6,4)
        pygame.draw.circle(s,(255,251,230),(45,43),4)
    elif tipo=='pocion':
        pygame.draw.rect(s,TINTA,(42,17,28,31),border_radius=5)
        pygame.draw.circle(s,TINTA,(56,66),33)
        pygame.draw.circle(s,(191,150,216),(56,66),28)
        pygame.draw.ellipse(s,(119,63,161),(30,55,52,38))
        pygame.draw.rect(s,(201,151,129),(44,17,24,12),border_radius=3)
        pygame.draw.circle(s,CREMA,(56,66),13)
        for dx in (-5,5):pygame.draw.circle(s,TINTA,(56+dx,64),4)
        pygame.draw.rect(s,CREMA,(49,74,14,7),border_radius=2)
        pygame.draw.line(s,(245,220,251),(37,45),(34,57),4)
    elif tipo=='bomba':
        pygame.draw.circle(s,TINTA,(56,66),33)
        pygame.draw.circle(s,(83,64,103),(56,66),28)
        pygame.draw.rect(s,TINTA,(46,28,20,13),border_radius=3)
        pygame.draw.lines(s,(235,189,138),False,[(56,29),(63,17),(76,22),(83,12)],4)
        pygame.draw.circle(s,(255,194,114),(83,12),7)
        for dx in (-9,9):
            pygame.draw.line(s,ROSA,(56+dx-4,59),(56+dx+4,67),3)
            pygame.draw.line(s,ROSA,(56+dx-4,67),(56+dx+4,59),3)
    else:
        puntos=[]
        for i in range(10):
            a=i*math.pi/5-math.pi/2;r=39 if i%2==0 else 18
            puntos.append((56+math.cos(a)*r,56+math.sin(a)*r))
        pygame.draw.polygon(s,TINTA,puntos)
        pygame.draw.polygon(s,(255,220,128),puntos,0)
        for dx in (-8,8):pygame.draw.ellipse(s,TINTA,(56+dx-2,48,4,10))
        pygame.draw.circle(s,CREMA,(43,35),4)
    return pygame.transform.smoothscale(s,(56,56))


def dibujar_objeto(pantalla,objeto,ahora):
    """Dibuja el objeto en su posición actual."""
    imagen=icono(objeto['tipo'],objeto.get('variante',0))
    pantalla.blit(imagen,imagen.get_rect(center=(round(objeto['x']),round(objeto['y']))))


def canasta(pantalla,x,y,recogidos=0,golpe=False):
    """Compone la canasta y sus estados visuales."""
    ilustracion=sprite('canasta',148,110)
    if ilustracion is not None:
        ilustracion=pygame.transform.smoothscale(ilustracion,(148,110))
        pantalla.blit(ilustracion,ilustracion.get_rect(midbottom=(round(x),round(y+59))))
        for j in range(min(20,recogidos)):
            fila=j//5;col=j%5
            mini=pygame.transform.smoothscale(icono('dulce',j%3),(20,20))
            pantalla.blit(mini,(round(x-48+col*19+(fila%2)*3),round(y-18-fila*8)))
        # La tela del frente queda delante del contenido.
        pantalla.blit(ilustracion,(round(x-74),round(y-4)),(0,47,148,63))
        return
    pygame.draw.arc(pantalla,(211,156,181),(x-45,y-45,90,72),0,math.pi,7)
    puntos=[(x-65,y),(x+65,y),(x+49,y+57),(x-49,y+57)]
    pygame.draw.polygon(pantalla,TINTA,puntos)
    pygame.draw.polygon(pantalla,(135,82,123),puntos,4)
    for j in range(min(4,recogidos)):
        mini=pygame.transform.smoothscale(icono('dulce',j%3),(27,27))
        pantalla.blit(mini,(x-47+j*24,y-8))
    pygame.draw.polygon(pantalla,(151,96,132),[(x-59,y+17),(x+59,y+17),(x+48,y+53),(x-48,y+53)])
    for i in range(5):
        pygame.draw.line(pantalla,(196,136,163),(x-42+i*21,y+20),(x-34+i*17,y+50),2)
    for yy in (y+29,y+42):pygame.draw.line(pantalla,(93,54,94),(x-52,yy),(x+52,yy),2)
    pygame.draw.rect(pantalla,(240,166,191),(x-66,y-2,132,12),border_radius=5)
    pygame.draw.circle(pantalla,(250,201,148) if not golpe else (177,128,207),(int(x),int(y+32)),11)
