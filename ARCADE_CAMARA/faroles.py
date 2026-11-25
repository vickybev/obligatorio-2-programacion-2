"""Minijuego 2: observar una secuencia y repetirla con la pinza."""
import math
import random
import pygame
from objetos_anime import sprite
from interfaz import cabecera, aviso, pie

LUGARES = [(220,245),(470,220),(730,245),(235,465),(480,490),(725,465)]
ROSA = (233,192,111)
CREMA = (247,239,210)


from ajustes import META_FAROLES, TIEMPO_FAROLES


class Faroles:
    """Administra las rondas de memoria de las constelaciones."""
    def __init__(self):
        """Prepara los faroles y la primera secuencia."""
        self.tiempo = TIEMPO_FAROLES
        self.puntos = 0
        self.meta = META_FAROLES
        self.fin = False
        self.eventos = []
        self.fase = 'mirar'
        self.reloj = 0.0
        self.paso = 0
        self.destello = 0.0
        self.ultimo = None
        self.malo = False
        self.nueva_secuencia()

    def nueva_secuencia(self):
        """Elige el orden de faroles para la ronda actual."""
        self.secuencia = random.sample(range(6),3+self.puntos)
        self.paso = 0
        self.fase = 'mirar'
        self.reloj = 0.0
        self.ultimo = None

    def encendido(self):
        """Indica el farol que corresponde iluminar en la fase actual."""
        if self.fase == 'mirar':
            t = self.reloj-.8
            indice = int(max(0,t)/.85)
            if t>=0 and indice<len(self.secuencia) and t%.85<.58:
                return self.secuencia[indice]
        if self.destello>0:
            return self.ultimo
        return None

    def actualizar(self, dt, pos, cerrada, mordida):
        """Alterna demostración y turno de juego, y comprueba cada pinza."""
        if self.fin or pos is None:
            return
        self.destello = max(0,self.destello-dt)
        if self.fase == 'mirar':
            anterior = self.encendido()
            self.reloj += dt
            actual = self.encendido()
            if actual is not None and actual != anterior:
                self.eventos.append(('captura',LUGARES[actual],0))
            if self.reloj >= .8+len(self.secuencia)*.85+.4:
                self.fase = 'repetir'
            return
        if self.fase == 'celebrar':
            self.reloj += dt
            if self.reloj>=1.15:
                if self.puntos>=self.meta:
                    self.fin = True
                else:
                    self.nueva_secuencia()
            return
        self.tiempo = max(0,self.tiempo-dt)
        if self.tiempo<=0:
            self.fin = True
            return
        if not mordida:
            return
        cerca = [i for i,p in enumerate(LUGARES) if math.dist(pos,p)<56]
        if not cerca:
            return
        elegido = cerca[0]
        self.ultimo = elegido
        self.destello = .38
        self.malo = elegido != self.secuencia[self.paso]
        if self.malo:
            self.tiempo = max(0,self.tiempo-4)
            self.eventos.append(('picadura',LUGARES[elegido],0))
            self.paso = 0
            self.fase = 'mirar'
            self.reloj = -.5
            if self.tiempo<=0:
                self.fin = True
        else:
            self.paso += 1
            self.eventos.append(('captura',LUGARES[elegido],0))
            if self.paso==len(self.secuencia):
                self.puntos += 1
                self.eventos.append(('entrega',LUGARES[elegido],self.puntos))
                self.fase = 'celebrar'
                self.reloj = 0.0

    def dibujar(self, pantalla, fuentes, ahora):
        """Dibuja los faroles, el recorrido acertado y el estado de la ronda."""
        def texto(contenido,pos,tam=24,color=CREMA):
            """Escribe un indicador de la pantalla con el estilo definido."""
            imagen=fuentes[tam].render(contenido,True,color)
            pantalla.blit(imagen,imagen.get_rect(center=pos))
        cabecera(pantalla,2,'Faroles del jardín',f'RONDA {min(self.puntos+1,4)} · MEMORIA',
                 'CONSTELACIONES',self.puntos,self.meta,self.tiempo)
        titulo='Mirá el orden' if self.fase=='mirar' else ('¡Constelación completa!' if self.fase=='celebrar' else 'Tu turno: repetí la secuencia')
        detalle='Cada farol encendido es una pista.' if self.fase=='mirar' else 'Cerrá y abrí la pinza sobre cada farol.'
        if self.malo and self.destello>0:detalle='¡Ups! −4 segundos. Mirá la secuencia otra vez.'
        aviso(pantalla,titulo,detalle)
        # Solo se revela el camino que ya acertaste.
        camino = self.secuencia if self.fase=='celebrar' else self.secuencia[:self.paso]
        if len(camino)>1:
            pygame.draw.lines(pantalla,ROSA,False,[LUGARES[i] for i in camino],3)
        encendido = self.encendido()
        for i,(x,y) in enumerate(LUGARES):
            activo=i==encendido or (self.fase=='celebrar' and i in self.secuencia)
            color=(255,222,150) if activo else (128,101,157)
            if activo:
                halo=pygame.Surface((150,150),pygame.SRCALPHA)
                for radio,alpha in ((70,15),(53,22),(38,40)):
                    pygame.draw.circle(halo,(*color,alpha),(75,75),radio)
                pantalla.blit(halo,(x-75,y-75))
            ilustracion=sprite('farol',94,110,not activo)
            if ilustracion is not None:
                pantalla.blit(ilustracion,ilustracion.get_rect(center=(x,y)))
                pygame.draw.circle(pantalla,(42,65,48),(x,y+49),15)
                texto(str(i+1),(x,y+49),22,CREMA)
            else:
                pygame.draw.line(pantalla,(93,74,108),(x,y-51),(x,y-35),3)
                pygame.draw.polygon(pantalla,(53,35,68),[(x-32,y-28),(x,y-43),(x+32,y-28)])
                pygame.draw.rect(pantalla,color,(x-26,y-28,52,63),border_radius=16)
                pygame.draw.rect(pantalla,(60,36,68),(x-26,y-28,52,63),3,border_radius=16)
                for dx in (-14,14):
                    pygame.draw.line(pantalla,(110,72,114),(x+dx,y-24),(x+dx,y+30),2)
                pygame.draw.rect(pantalla,(68,42,77),(x-28,y+28,56,6),border_radius=3)
                texto(str(i+1),(x,y+2),28,(48,28,57))
            if activo:
                for j in range(4):
                    ang=ahora*2+j*math.tau/4
                    pygame.draw.circle(pantalla,color,(int(x+math.cos(ang)*45),int(y+math.sin(ang)*43)),2)
        for i in range(len(self.secuencia)):
            x=480+(i-(len(self.secuencia)-1)/2)*27
            pygame.draw.circle(pantalla,ROSA if i<self.paso else (89,111,80),(int(x),573),7)
        pie(pantalla,'Encendé cuatro constelaciones','Abrí la pinza entre faroles. El tiempo corre solo durante tu turno.')



def cursor(pantalla,pos,cerrada,ahora):
    """Dibuja la estrella que sigue a la mano."""
    x,y=pos
    color=ROSA if cerrada else CREMA
    # Dos bordes opuestos mantienen el cursor visible sobre papel y bosque.
    pygame.draw.circle(pantalla,(25,49,40),(int(x),int(y)),21,5)
    pygame.draw.circle(pantalla,color,(int(x),int(y)),18,2)
    puntos=[]
    for i in range(10):
        ang=i*math.pi/5-math.pi/2
        radio=12 if i%2==0 else 5
        puntos.append((x+math.cos(ang)*radio,y+math.sin(ang)*radio))
    pygame.draw.polygon(pantalla,color,puntos)
    pygame.draw.polygon(pantalla,(25,49,40),puntos,2)
    pygame.draw.circle(pantalla,(25,49,40),(round(x),round(y)),2)
