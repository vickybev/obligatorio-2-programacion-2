"""Colección local: una partida se registra una vez al llegar al resultado."""
import json
import os
import math
from pathlib import Path
import pygame
from interfaz import papel, escribir, MUSGO, TINTA, PAPEL, boton, separador
from personajes import variante
from objetos_anime import sprite
from arte_sellos import sprite as sprite_magico

NOMBRES=('Bichos a la boca','Faroles del jardín','Banquete del familiar','Sellos de luna')
SELLOS=('Amiga del bosque','Guardiana de la luz','Dulzura de hogar','Tejedora de estrellas')
RECUERDOS=('Mariposa de miel','Farol del crepúsculo','Dulce de la casita','Espíritu de luna')
HISTORIAS=(('Guardaste un pedacito','de sol entre tus manos.'),('Una lucecita que recuerda','el camino de regreso.'),('Una receta secreta,','un poquito de felicidad.'),('Dibujaste un camino','y la luna lo siguió.'))
REPETIR=pygame.Rect(111,532,350,58)
VOLVER=pygame.Rect(499,532,350,58)
DIARIO_MENU=pygame.Rect(1050,67,205,73)


class Diario:
    def __init__(self,ruta=None):
        self.ruta=Path(ruta or os.environ.get('CASITA_DATOS',Path(__file__).parent/'datos'/'diario.json'))
        self.datos={str(i):dict(partidas=0,victorias=0,mejor=0) for i in range(1,5)}
        self.error=''
        self.giros=[0.0]*4
        if self.ruta.exists():
            try:
                contenido=json.loads(self.ruta.read_text(encoding='utf-8'))
                if not isinstance(contenido,dict): raise ValueError('Formato desconocido')
                if contenido.get('version')!=1: raise ValueError('Versión desconocida')
                for k in self.datos:
                    fila=contenido['juegos'][k]
                    if not isinstance(fila,dict): raise ValueError('Fila inválida')
                    if any(type(fila.get(c)) is not int or fila[c]<0 for c in self.datos[k]):
                        raise ValueError('Datos inválidos')
                    if fila['victorias']>fila['partidas']: raise ValueError('Victorias inválidas')
                self.datos=contenido['juegos']
            except (ValueError,KeyError,TypeError,OSError):
                self.error='No se pudo leer el diario. Conservamos el archivo original.'

    @property
    def sellos(self):
        return sum(d['victorias']>0 for d in self.datos.values())

    def registrar(self,juego,partida):
        if getattr(partida,'_diario_registrado',False): return
        partida._diario_registrado=True
        d=self.datos[str(juego)]
        gano=partida.puntos>=partida.meta
        partida._sello_nuevo=gano and d['victorias']==0
        d['partidas']+=1
        d['victorias']+=int(gano)
        d['mejor']=max(d['mejor'],int(partida.puntos))
        # Si el original era ilegible no lo reemplazamos con datos parciales.
        if self.error: return
        temporal=self.ruta.with_suffix('.tmp')
        try:
            self.ruta.parent.mkdir(parents=True,exist_ok=True)
            temporal.write_text(json.dumps({'version':1,'juegos':self.datos},ensure_ascii=False,indent=2),encoding='utf-8')
            temporal.replace(self.ruta)
        except OSError:
            self.error='No se pudo guardar. Tu progreso sigue disponible en esta sesión.'

    def boton_menu(self,s,pos=None):
        papel(s,DIARIO_MENU)
        escribir(s,'Mi diario',(1152,92),25,titulo=True,ancho=180)
        escribir(s,f'D · {self.sellos}/4 sellos',(1152,119),18,negrita=True)
        if pos and DIARIO_MENU.collidepoint(pos):
            pygame.draw.rect(s,MUSGO,DIARIO_MENU,3,border_radius=12)

    def insignias(self,s,rects):
        for i,r in enumerate(rects,1):
            if self.datos[str(i)]['victorias']:
                sello(s,(r.right-27,r.top+31),19,i)

    def album(self,s,coleccion,pos=None,dt=1/30):
        papel(s,(38,24,884,626))
        escribir(s,'El tesoro de mis aventuras',(480,64),40,titulo=True)
        escribir(s,f'{self.sellos} / 4 recuerdos · Acercá la mano y descubrí su historia',(480,108),20,ancho=810)
        tiempo=pygame.time.get_ticks()/1000
        for i in range(4):
            x=65+(i%2)*425; y=137+(i//2)*210
            d=self.datos[str(i+1)]; obtenido=d['victorias']>0
            encima=pos is not None and pygame.Rect(x,y,405,190).collidepoint(pos)
            objetivo=1 if encima and obtenido else 0
            self.giros[i]+=max(-dt*2.5,min(dt*2.5,objetivo-self.giros[i]))
            giro=self.giros[i]
            tarjeta=pygame.Surface((405,190),pygame.SRCALPHA)
            papel(tarjeta,(0,0,405,185),((236,225,185),(221,230,203),(241,218,190),(218,229,224))[i] if obtenido else (225,220,200))
            # Cintas y número de pieza, como un recuerdo pegado al cuaderno.
            for tx in (18,348):
                pygame.draw.polygon(tarjeta,(194,178,132),[(tx,2),(tx+35,6),(tx+31,18),(tx-3,14)])
            if giro<.5:
                recuerdo(tarjeta,(92,90),i,112,obtenido,tiempo)
                escribir(tarjeta,f'NO. 0{i+1}',(92,163),16,negrita=True)
                escribir(tarjeta,RECUERDOS[i] if obtenido else 'Un secreto del bosque',(278,48),27,titulo=True,ancho=235)
                escribir(tarjeta,SELLOS[i] if obtenido else 'Todavía está dormido',(278,91),18,negrita=True,ancho=235)
                escribir(tarjeta,'En tu colección' if obtenido else 'Completá esta aventura',(278,130),18,ancho=235)
                escribir(tarjeta,NOMBRES[i],(278,159),17,ancho=235)
            else:
                escribir(tarjeta,RECUERDOS[i],(202,37),29,titulo=True,ancho=365)
                for j,linea in enumerate(HISTORIAS[i]): escribir(tarjeta,linea,(202,82+j*27),21)
                escribir(tarjeta,f'Mejor marca: {d["mejor"]} · {d["victorias"]} victorias',(202,151),18)
            ancho=max(3,round(405*abs(math.cos(giro*math.pi))))
            tarjeta=pygame.transform.smoothscale(tarjeta,(ancho,190))
            s.blit(tarjeta,(x+(405-ancho)//2,y))
        escribir(s,self.error or ('¡La casita está llena de recuerdos!' if self.sellos==4 else 'Cada aventura completada despierta un tesoro nuevo.'),(480,583),23,titulo=True,ancho=820)
        boton(s,(330,607,300,38),'Volver a las aventuras · Esc')
        return pygame.Rect(330,607,300,38)

    def resultado(self,s,juego,partida,tiempo):
        self.registrar(juego,partida)
        gano=partida.puntos>=partida.meta
        if not hasattr(partida,'_revelado_en'): partida._revelado_en=tiempo
        aparicion=min(1,max(0,(tiempo-partida._revelado_en)/.8))
        aparicion=1-(1-aparicion)**3
        papel(s,(40,28,880,620))
        pygame.draw.line(s,(184,174,138),(480,145),(480,490),2)
        escribir(s,'Diario de pequeñas magias',(480,66),32,titulo=True)
        escribir(s,NOMBRES[juego-1],(480,108),23,negrita=True)
        recuerdo(s,(263,260),juego-1,round(85+70*aparicion),gano,tiempo)
        escribir(s,SELLOS[juego-1] if gano else 'La magia se practica',(263,365),25,titulo=True,ancho=355)
        escribir(s,RECUERDOS[juego-1] if gano else 'Cada intento te enseña algo.',(263,406),23,titulo=True,ancho=355)
        escribir(s,('¡Un nuevo recuerdo!' if getattr(partida,'_sello_nuevo',False) else '¡Lo lograste!') if gano else 'Probemos otra vez',(668,190),31,titulo=True,ancho=330)
        escribir(s,f'{partida.puntos} / {partida.meta}',(668,258),49,negrita=True)
        escribir(s,'Tu resultado',(668,301),20)
        escribir(s,f'Mejor marca: {self.datos[str(juego)]["mejor"]}',(668,354),23,negrita=True)
        escribir(s,f'{self.sellos} de 4 recuerdos reunidos',(668,400),20)
        escribir(s,'¡El diario está completo!' if self.sellos==4 else 'La casita guarda tus aventuras.',(480,476),22,titulo=True)
        for rect,label in ((REPETIR,'Otra ronda · Enter'),(VOLVER,'Elegir aventura · Esc')):
            boton(s,rect,label)
        escribir(s,self.error or 'D: ver mi diario · Progreso guardado en esta PC',(480,619),17,ancho=820)
        if gano:
            for i in range(16):
                a=i*math.tau/16+tiempo*.25
                r=92+7*math.sin(tiempo*2+i)
                estrella(s,(263+math.cos(a)*r,260+math.sin(a)*r),5,(174,137,63))


def recuerdo(s,pos,indice,lado,obtenido,tiempo):
    x,y=pos
    imagen=(variante('polilla',lado,0) if indice==0 else sprite('farol' if indice==1 else 'dulce',lado,lado) if indice in (1,2) else sprite_magico('espiritu',lado))
    if imagen is None:return
    if not obtenido:
        silueta=pygame.mask.from_surface(imagen).to_surface(setcolor=(153,158,133,255),unsetcolor=(0,0,0,0))
        s.blit(silueta,silueta.get_rect(center=(round(x),round(y))))
        escribir(s,'?',(x,y),48,PAPEL,titulo=True)
        return
    for j in range(8):
        a=j*math.tau/8+tiempo*.3
        radio=lado*.55+math.sin(tiempo*2+j)*4
        estrella(s,(x+math.cos(a)*radio,y+math.sin(a)*radio),3+(j%2),(176,139,56))
    imagen=pygame.transform.rotozoom(imagen,math.sin(tiempo*1.4+indice)*5,1+.025*math.sin(tiempo*2))
    borde=pygame.mask.from_surface(imagen).to_surface(setcolor=(255,248,224,255),unsetcolor=(0,0,0,0))
    r=imagen.get_rect(center=(round(x),round(y+math.sin(tiempo*2+indice)*4)))
    for dx,dy in ((-3,0),(3,0),(0,-3),(0,3)):s.blit(borde,r.move(dx,dy))
    s.blit(imagen,r)


def estrella(s,pos,r,color):
    x,y=pos
    pygame.draw.polygon(s,color,[(x+math.cos(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.43),y+math.sin(-math.pi/2+i*math.pi/5)*(r if i%2==0 else r*.43)) for i in range(10)])


def sello(s,pos,r,numero,activo=True):
    x,y=map(round,pos); color=(100,130,88) if activo else (166,161,140)
    pygame.draw.circle(s,(222,211,167),(x,y),r+4)
    pygame.draw.circle(s,color,(x,y),r)
    pygame.draw.circle(s,PAPEL,(x,y),r-5,2)
    if numero==1:
        pygame.draw.ellipse(s,PAPEL,(x-r*.55,y-r*.4,r*1.1,r*.8))
        pygame.draw.line(s,color,(x-r*.4,y+r*.2),(x+r*.4,y-r*.2),2)
    elif numero==2:
        pygame.draw.rect(s,PAPEL,(x-r*.35,y-r*.48,r*.7,r*.96),border_radius=max(2,r//7))
        pygame.draw.line(s,color,(x,y-r*.4),(x,y+r*.4),2)
    elif numero==3:
        pygame.draw.circle(s,PAPEL,(x,y),round(r*.47))
        for dx,dy in ((-.15,-.18),(.2,.05),(-.12,.24)):
            pygame.draw.circle(s,color,(round(x+dx*r),round(y+dy*r)),max(2,r//12))
    else: estrella(s,(x,y),r*.6,PAPEL)
