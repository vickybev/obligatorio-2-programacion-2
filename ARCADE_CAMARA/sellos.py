"""Minijuego 4: trazar sellos guiados con la pinza para liberar espíritus."""
import math
import pygame
from personajes import variante
from arte_sellos import sprite
from interfaz import cabecera, aviso, pie, papel, escribir

ROSA=(233,192,111)
CREMA=(247,239,210)


def remuestrear(vertices,paso=17):
    resultado=[]
    for a,b in zip(vertices,vertices[1:]):
        n=max(1,math.ceil(math.dist(a,b)/paso))
        resultado.extend([(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n)])
    return resultado+[vertices[-1]]


def simbolo_base(indice):
    cx,cy=480,380
    if indice==0:
        return 'CÍRCULO',[(cx+125*math.sin(i*math.tau/42),cy-125*math.cos(i*math.tau/42)) for i in range(43)]
    if indice==1:
        return 'TRIÁNGULO',remuestrear([(480,240),(620,500),(340,500),(480,240)])
    if indice==2:
        puntos=[]
        for i in range(61):
            t=math.pi+i*math.tau/60
            x=16*math.sin(t)**3
            y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
            puntos.append((cx+x*8,cy-y*8))
        return 'CORAZÓN',puntos
    vertices=[]
    for i in range(11):
        a=i*math.pi/5-math.pi/2;r=140 if i%2==0 else 61
        vertices.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    return 'ESTRELLA',remuestrear(vertices)


def simbolo(indice):
    nombre,puntos=simbolo_base(indice)
    return nombre,[(480+(x-480)*1.06,380+(y-380)*1.06) for x,y in puntos]


class Sellos:
    def __init__(self):
        self.tiempo=90.0
        self.puntos=0
        self.meta=4
        self.fin=False
        self.eventos=[]
        self.celebracion=0.0
        self.nombre,self.guia=simbolo(0)
        self.paso=0
        self.trazo=[]
        self.dibujando=False
        self.iniciado=False
        self.punta=None

    def reiniciar_trazo(self):
        if self.celebracion or self.fin:
            return
        self.paso=0
        self.trazo=[]
        self.iniciado=False
        self.dibujando=False
        self.punta=None

    def actualizar(self,dt,pos,cerrada,mordida=False):
        if self.fin or pos is None:
            self.dibujando=False
            self.punta=None
            return
        if self.punta is None:
            self.punta=tuple(pos)
        elif math.dist(pos,self.punta)>4:
            distancia=math.dist(pos,self.punta)
            respuesta=.19 if distancia<20 else .07
            alpha=1-math.exp(-max(dt,.001)/respuesta)
            alpha=min(alpha,900*max(dt,0)/distancia)
            self.punta=tuple(a+(b-a)*alpha for a,b in zip(self.punta,pos))
        pos=self.punta
        if self.celebracion>0:
            self.celebracion=max(0,self.celebracion-dt)
            if self.celebracion==0:
                if self.puntos==self.meta:
                    self.fin=True
                else:
                    self.nombre,self.guia=simbolo(self.puntos)
                    self.reiniciar_trazo()
            return
        self.tiempo=max(0,self.tiempo-dt)
        if self.tiempo<=0:
            self.fin=True
            return
        if not cerrada:
            self.dibujando=False
            return
        if not self.iniciado:
            if math.dist(pos,self.guia[0])>=29:
                return
            self.iniciado=True
        if not self.dibujando:
            self.trazo.append(None)
        self.dibujando=True
        if not self.trazo or self.trazo[-1] is None or math.dist(pos,self.trazo[-1])>3:
            self.trazo.append(tuple(pos))
            self.eventos.append(("polvo",tuple(pos),0))
            self.trazo=self.trazo[-1800:]
        anterior=self.paso
        while self.paso<len(self.guia) and math.dist(pos,self.guia[self.paso])<29:
            self.paso+=1
        if self.paso>anterior and self.paso//7!=anterior//7:
            self.eventos.append(('captura',tuple(pos),0))
        if self.paso==len(self.guia):
            self.puntos+=1
            self.celebracion=1.2
            self.dibujando=False
            self.eventos.append(('entrega',tuple(pos),self.puntos))

    def dibujar(self,pantalla,fuentes,ahora):
        def texto(contenido,pos,tam=24,color=CREMA):
            imagen=fuentes[tam].render(contenido,True,color)
            pantalla.blit(imagen,imagen.get_rect(center=pos))
        estado='BUSCÁ LA JOYA' if not self.iniciado else ('TRAZANDO MAGIA' if self.dibujando else 'PLUMA LEVANTADA')
        cabecera(pantalla,4,'Sellos de luna',estado,'ESPÍRITUS LIBERADOS',self.puntos,self.meta,self.tiempo)
        detalle='Seguí la joya manteniendo la pinza.' if self.iniciado else 'Acercate al inicio y cerrá la pinza.'
        aviso(pantalla,'¡Espíritu liberado!' if self.celebracion else self.nombre.capitalize(),detalle)
        # Superficie oscura uniforme: separa la magia del fondo y de la cámara.
        pygame.draw.circle(pantalla,(185,196,145),(480,380),217,2)
        marco=sprite("marco",440)
        if marco is not None:
            pantalla.blit(marco,marco.get_rect(center=(480,380)))
        else:
            pygame.draw.circle(pantalla,(100,77,122),(480,380),168,1)
            pygame.draw.circle(pantalla,(100,77,122),(480,380),175,1)
        # Disco limpio: las hojas quedan fuera del espacio del recorrido.
        for j in range(12):
            a=j*math.tau/12+ahora*.025
            pygame.draw.circle(pantalla,(201,154,185),(int(480+math.cos(a)*210),int(380+math.sin(a)*210)),2)
        if len(self.guia)>1:
            pygame.draw.lines(pantalla,(13,29,29),False,self.guia,9)
            pygame.draw.lines(pantalla,(204,220,197),False,self.guia,4)
        for i,p in enumerate(self.guia):
            if i%3==0:
                pygame.draw.circle(pantalla,ROSA if i<self.paso else (233,239,215),(round(p[0]),round(p[1])),3)
        segmento=[]
        for p in self.trazo+[None]:
            if p is None:
                if len(segmento)>1:
                    pygame.draw.lines(pantalla,(8,22,26),False,segmento,15)
                    pygame.draw.lines(pantalla,(255,185,65),False,segmento,9)
                    pygame.draw.lines(pantalla,(255,249,220),False,segmento,3)
                segmento=[]
            else:
                segmento.append(p)
        imagen=sprite('espiritu',87)
        if imagen is None:
            imagen=variante('polilla',66,0)
        if imagen:
            yy=380-(1.2-self.celebracion)*75 if self.celebracion else 380+math.sin(ahora*2)*4
            pantalla.blit(imagen,imagen.get_rect(center=(480,round(yy))))
        if not self.celebracion:
            pygame.draw.circle(pantalla,(163,196,160),(480,380),48,2)
            objetivo=self.guia[min(self.paso,len(self.guia)-1)]
            centro=tuple(map(round,objetivo))
            pygame.draw.circle(pantalla,(12,29,28),centro,29)
            pygame.draw.circle(pantalla,(255,209,97),centro,26,4)
            pygame.draw.circle(pantalla,(255,248,214),centro,30,2)
            if not self.iniciado:
                papel(pantalla,(objetivo[0]+37,objetivo[1]-18,116,36))
                escribir(pantalla,"INICIO",(objetivo[0]+95,objetivo[1]),20,negrita=True)
            joya=sprite("joya",44)
            if joya is not None:
                pantalla.blit(joya,joya.get_rect(center=tuple(map(round,objetivo))))
            else:
                pygame.draw.circle(pantalla,ROSA,tuple(map(round,objetivo)),14,3)
            pygame.draw.circle(pantalla,CREMA,tuple(map(round,objetivo)),3)
        else:
            for j in range(12):
                a=j*math.tau/12+ahora
                r=80+(1.2-self.celebracion)*80
                pygame.draw.circle(pantalla,(255,216,153),(int(480+math.cos(a)*r),int(380+math.sin(a)*r)),3)
        porcentaje=round(self.paso/len(self.guia)*100)
        papel(pantalla,(740,537,200,64))
        escribir(pantalla,f'Sello {min(self.puntos+1,4)} · {porcentaje}%',(840,559),20,negrita=True)
        pygame.draw.rect(pantalla,(69,46,83),(760,584,160,6),border_radius=3)
        if porcentaje:
            pygame.draw.rect(pantalla,ROSA,(760,584,round(160*porcentaje/100),6),border_radius=3)
        pie(pantalla,'Tu magia comienza en la joya','Abrí la pinza para levantar la pluma y continuar después.',borrar=True)
