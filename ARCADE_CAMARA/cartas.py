"""Colección de cuatro cartas con giro reversible al pasar mouse o mano."""
import math
from pathlib import Path
import pygame
from identidad import fuente
from interfaz import lectura
from objetos_anime import sprite
from personajes import variante
from arte_sellos import sprite as sprite_sello

CREMA=(246,239,214)
ORO=(153,167,118)
ROSA=(201,143,140)
DATOS=[
    (['Bichos a la boca'],'CAPTURA',['Atrapá con la pinza.','Llevalo a la bolsita.','Evitá los violetas.'],'8 bichitos · 60 segundos'),
    (['Faroles del jardín'],'MEMORIA',['Mirá las luces.','Recordá su orden.','Repetí con la pinza.'],'4 constelaciones'),
    (['Banquete del','familiar'],'REFLEJOS',['Mové la canasta.','Atrapá dulces y estrellas.','Esquivá los peligros.'],'40 puntos · 60 segundos'),
    (['Sellos de luna'],'TRAZO MÁGICO',['Acercate a la joya.','Dibujá con la pinza.','Liberá los espíritus.'],'4 sellos · 90 segundos'),
]


class Coleccion:
    def __init__(self):
        self.rects=[pygame.Rect(120+i*270,205,230,365) for i in range(4)]
        self.giros=[0.0]*4
        self.encima=[False]*4
        self.t=0.0
        self.frentes=[]
        self.dorsos=[]
        self.fuentes={n:lectura(n,True) for n in (18,20,22,24,28)}
        self.titulo=pygame.font.Font('C:/Windows/Fonts/Gabriola.ttf',30)
        ruta=Path(__file__).parent/'assets'/'cartas-bosque-v2.png'
        atlas=pygame.image.load(str(ruta)).convert() if ruta.exists() else None
        for i in range(4):
            self.frentes.append(self.crear_frente(i,atlas))
            self.dorsos.append(self.crear_dorso(i))

    def texto(self,s,contenido,y,tam=20,color=CREMA,titulo=False):
        fuente=self.titulo if titulo else self.fuentes[tam]
        imagen=fuente.render(contenido,True,color)
        # Ajustar títulos largos preservando legibilidad dentro de la carta.
        if imagen.get_width()>174:
            imagen=pygame.transform.smoothscale(imagen,(174,imagen.get_height()))
        s.blit(imagen,imagen.get_rect(center=(100,y)))

    def marco(self,s):
        pygame.draw.rect(s,ORO,(2,2,196,350),2,border_radius=15)
        pygame.draw.rect(s,(178,176,141),(8,8,184,338),1,border_radius=11)
        for x,y in ((16,17),(184,17),(16,337),(184,337)):
            pygame.draw.polygon(s,ORO,[(x,y-5),(x+4,y),(x,y+5),(x-4,y)])

    def crear_frente(self,i,atlas):
        s=pygame.Surface((200,354),pygame.SRCALPHA)
        pygame.draw.rect(s,(55,72,57),(0,0,200,354),border_radius=15)
        if atlas is not None:
            w,h=atlas.get_size();col=i%2;fila=i//2
            x0,x1=round(col*w/2),round((col+1)*w/2)
            y0,y1=round(fila*h/2),round((fila+1)*h/2)
            imagen=pygame.transform.smoothscale(atlas.subsurface((x0,y0,x1-x0,y1-y0)),(196,350))
            s.blit(imagen,(2,2))
        velo=pygame.Surface((180,95),pygame.SRCALPHA)
        for y in range(95):
            pygame.draw.line(velo,(34,56,41,min(240,40+y*3)),(0,y),(180,y))
        s.blit(velo,(10,249))
        lineas=DATOS[i][0]
        for j,linea in enumerate(lineas):
            self.texto(s,linea,279+j*24-(12 if len(lineas)>1 else 0),titulo=True)
        self.texto(s,DATOS[i][1],321,18,(222,228,187))
        pygame.draw.circle(s,(55,72,57),(28,30),15)
        numero=self.fuentes[20].render(str(i+1),True,CREMA)
        s.blit(numero,numero.get_rect(center=(28,30)))
        self.marco(s)
        return s

    def crear_dorso(self,i):
        s=pygame.Surface((200,354),pygame.SRCALPHA)
        pygame.draw.rect(s,(240,232,207),(0,0,200,354),border_radius=15)
        for y in range(22,335,12):
            for x in range(18,190,14):
                pygame.draw.circle(s,(219,216,187),(x,y),1)
        self.marco(s)
        self.texto(s,f'0{i+1} / {DATOS[i][1]}',31,18,(73,99,70))
        imagen=pygame.transform.smoothscale(self.frentes[i].subsurface((20,30,160,190)),(68,81))
        s.blit(imagen,imagen.get_rect(center=(100,91)))
        for j,linea in enumerate(DATOS[i][2]):self.texto(s,linea,164+j*26,20,(52,76,55))
        self.texto(s,DATOS[i][3],254,18,(81,103,70))
        pygame.draw.rect(s,(111,139,103),(21,278,158,40),border_radius=9)
        self.texto(s,'JUGAR',299,24,(247,241,217))
        self.texto(s,'Clic o cerrá la pinza',333,18,(73,99,70))
        return s

    def actualizar(self,dt,punteros):
        self.t+=dt
        for i,rect in enumerate(self.rects):
            # El área de interacción permanece estable durante todo el giro.
            zona=rect.inflate(8,34)
            self.encima[i]=any(p is not None and zona.collidepoint(p) for p in punteros)
            objetivo=1.0 if self.encima[i] else 0.0
            paso=dt/.46
            self.giros[i]=min(objetivo,self.giros[i]+paso) if objetivo>self.giros[i] else max(objetivo,self.giros[i]-paso)

    def seleccionar(self,puntero):
        if puntero is not None:
            for i,rect in enumerate(self.rects):
                if rect.inflate(8,34).collidepoint(puntero):return i+1
        return None

    def dibujar(self,pantalla):
        for i,rect in enumerate(self.rects):
            t=self.giros[i]
            suavizado=t*t*(3-2*t)
            ancho=max(3,round(rect.w*abs(math.cos(math.pi*suavizado))))
            cara=self.frentes[i] if t<.5 else self.dorsos[i]
            imagen=pygame.transform.smoothscale(cara,(ancho,rect.h))
            inclinacion=math.sin(math.pi*suavizado)*2*(-1 if i%2 else 1)
            imagen=pygame.transform.rotate(imagen,inclinacion)
            elevacion=round(12*suavizado)
            destino=imagen.get_rect(center=(rect.centerx,rect.centery-elevacion))
            sombra=pygame.Surface((rect.w+16,rect.h+20),pygame.SRCALPHA)
            pygame.draw.rect(sombra,(24,38,25,85),(8,10,rect.w,rect.h),border_radius=18)
            pantalla.blit(sombra,(rect.x-3,rect.y+4-elevacion))
            pantalla.blit(imagen,destino)
            if self.encima[i] and t>.95:
                pygame.draw.rect(pantalla,(160,191,137),destino.inflate(5,5),1,border_radius=16)


class Carrusel(Coleccion):
    """Una carta visible, con barrido lateral y un gesto por movimiento."""
    def __init__(self):
        super().__init__()
        self.frentes_grandes=[pygame.transform.smoothscale(im,(280,475)) for im in self.frentes]
        self.indice=0
        self.anterior=0
        self.transicion=1.0
        self.direccion=1
        self.carta=pygame.Rect(500,151,280,475)
        self.izquierda=pygame.Rect(360,345,76,76)
        self.derecha=pygame.Rect(844,345,76,76)
        self.ancla=None
        self.edad=0
        self.espera=0
        self.bloqueado=False
        self.permanencia=0.0
        self.previa=None
        self.listo=False
        self.centro_seleccion=None
        self.lado_origen=0
        self.ausencia=0
        self.rects=[pygame.Rect(-1000,-1000,1,1) for _ in range(4)]

    def mover(self,direccion):
        if self.transicion<1:return
        self.anterior=self.indice
        self.indice=(self.indice+direccion)%4
        self.direccion=direccion
        self.transicion=0
        self.espera=.8
        self.ancla=None
        self.permanencia=0
        self.listo=False
        self.lado_origen=0

    def actualizar(self,dt,punteros,gesto=False,cerrada=False):
        self.t+=dt
        self.transicion=min(1,self.transicion+dt/.48)
        self.espera=max(0,self.espera-dt)
        self.rects=[pygame.Rect(-1000,-1000,1,1) for _ in range(4)]
        self.rects[self.indice]=self.carta.copy()
        p=punteros[0] if punteros else None
        estable=p is not None and (self.centro_seleccion is None or math.dist(p,self.centro_seleccion)<24)
        if not estable or self.centro_seleccion is None:
            self.centro_seleccion=p
        self.previa=p
        dentro=p is not None and self.carta.collidepoint(p)
        self.permanencia=self.permanencia+dt if dentro and estable and gesto and self.transicion>=1 else 0
        self.listo=self.permanencia>=1.5
        if not gesto or p is None:
            self.ancla=None
            self.ausencia+=dt
            if self.ausencia>.35:self.lado_origen=0
            return
        self.ausencia=0
        # Barrido espacial sobre la carta: no depende de velocidad ni postura.
        if not pygame.Rect(0,self.carta.top-40,1280,self.carta.height+80).collidepoint(p):
            self.lado_origen=0
            return
        if self.transicion<1:return
        lado=-1 if p[0]<self.carta.centerx-35 else (1 if p[0]>self.carta.centerx+35 else 0)
        if lado and not self.lado_origen:
            self.lado_origen=lado
        elif lado and lado!=self.lado_origen:
            self.mover(-1 if lado==1 else 1)

    def seleccionar(self,puntero):
        if puntero is None:return None
        if self.izquierda.collidepoint(puntero):self.mover(-1)
        elif self.derecha.collidepoint(puntero):self.mover(1)
        elif self.carta.collidepoint(puntero) and self.transicion>=1:return self.indice+1
        return None

    def dibujar(self,pantalla):
        from interfaz import escribir, PAPEL, MUSGO
        t=self.transicion;t=t*t*(3-2*t)
        # Recorte local: la carta que sale nunca tapa el logo ni los controles.
        anterior_clip=pantalla.get_clip()
        pantalla.set_clip((245,142,790,490))
        indices=[(self.indice,0)] if self.transicion>=1 else [(self.anterior,-self.direccion*t*650),(self.indice,self.direccion*(1-t)*650)]
        for i,desplazamiento in indices:
            r=self.carta.move(round(desplazamiento),round(math.sin(self.t*1.4)*3))
            sombra=pygame.Surface((r.w+20,r.h+20),pygame.SRCALPHA)
            pygame.draw.rect(sombra,(21,40,27,80),(9,9,r.w,r.h),border_radius=18)
            pantalla.blit(sombra,(r.x-3,r.y))
            imagen=self.frentes_grandes[i]
            pantalla.blit(imagen,r)
            if i==self.indice and self.transicion>=1 and self.permanencia>0:
                progreso=min(1,self.permanencia/1.5)
                alto=round(r.height*progreso)
                luz=pygame.Surface((r.width,alto),pygame.SRCALPHA)
                luz.fill((249,216,124,85))
                pantalla.blit(luz,(r.x,r.bottom-alto))
                pygame.draw.line(pantalla,(255,235,158),(r.left+5,r.bottom-alto),(r.right-5,r.bottom-alto),3)
                pygame.draw.rect(pantalla,(247,220,142),r,3,border_radius=14)
        pantalla.set_clip(anterior_clip)
        for r,lado in ((self.izquierda,-1),(self.derecha,1)):
            pygame.draw.circle(pantalla,PAPEL,r.center,34)
            pygame.draw.circle(pantalla,MUSGO,r.center,34,2)
            x,y=r.center
            pygame.draw.lines(pantalla,MUSGO,False,[(x-lado*7,y-13),(x+lado*7,y),(x-lado*7,y+13)],3)
        for i in range(4):
            pygame.draw.circle(pantalla,MUSGO if i==self.indice else PAPEL,(604+i*24,645),5)


def cursor(pantalla,pos,cerrada):
    x,y=map(round,pos)
    pygame.draw.circle(pantalla,(28,52,42),(x,y),12)
    pygame.draw.circle(pantalla,(255,232,166),(x,y),9)
    pygame.draw.circle(pantalla,(28,52,42),(x,y),3)
