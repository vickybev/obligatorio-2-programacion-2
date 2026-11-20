"""Demostraciones visuales en bucle; no modifican las partidas ni emiten audio."""
import math
from functools import lru_cache
import pygame
from personajes import dibujar_familiar, dibujar_bicho
from objetos_anime import sprite
from arte_sellos import sprite as magia
from bolsa import ilustracion
from gestos import mano_lateral


def mezclar(a,b,t):
    t=max(0,min(1,t));t=t*t*(3-2*t)
    return a+(b-a)*t


def poner(s,im,pos):
    if im is not None: s.blit(im,im.get_rect(center=tuple(map(round,pos))))


def pinza(s,pos,cerrada):
    mano_lateral(s,(pos[0]-4,pos[1]+9),float(cerrada),64)


@lru_cache(maxsize=1)
def bolsita():
    im=ilustracion()
    return pygame.transform.smoothscale(im,(90,73)) if im is not None else None


def dibujar(s,juego,paso,tiempo):
    # Lienzo local de 240x110: todo permanece dentro de la ilustración del paso.
    t=tiempo%4
    if juego==1:
        if paso==0:
            x=mezclar(48,107,t/2.2)
            dibujar_familiar(s,(x,59),False,tiempo)
            dibujar_bicho(s,(164+math.sin(t*3)*8,50),False,tiempo,.65)
            pinza(s,(210,28),False)
        elif paso==1:
            cerrada=1.65<t<3.45
            dibujar_familiar(s,(83,57),cerrada,tiempo)
            if t<1.85:
                u=max(0,(t-.5)/1.35)
                dibujar_bicho(s,(mezclar(181,85,u),mezclar(46,74,u)),False,tiempo,.65)
            if 1.85<t<3.15:
                for i in range(5):
                    a=i*math.tau/5+t
                    pygame.draw.circle(s,(190,143,57),(round(83+math.cos(a)*48),round(57+math.sin(a)*44)),3)
            pinza(s,(210,28),max(0,min(1,(t-1.45)/.3,(3.65-t)/.2)))
        else:
            poner(s,bolsita(),(177,68))
            x=mezclar(55,116,t/1.7)
            cerrada=t<2.2
            dibujar_familiar(s,(x,54),cerrada,tiempo)
            if t<2.2: dibujar_bicho(s,(x+26,77),False,tiempo,.4)
            elif t<3.1:
                dibujar_bicho(s,(mezclar(143,177,(t-2.2)/.5),mezclar(55,63,(t-2.2)/.9)),False,tiempo,.4)
            else: dibujar_bicho(s,(177,63),False,tiempo,.35)
            # La tela delantera tapa solo la parte inferior del bichito.
            im=bolsita()
            if im is not None: s.blit(im,(132,69),(0,37,90,36))
            pinza(s,(214,20),cerrada)
    elif juego==2:
        ordre=(0,2,1);actuel=min(2,int(t/.85)) if t<2.55 else -1
        for i in range(3):
            x=45+i*72;actif=actuel>=0 and ordre[actuel]==i
            if actif: pygame.draw.circle(s,(238,207,135),(x,54),32)
            poner(s,sprite('farol',48,65,not actif),(x,54))
            if paso==1:
                im=pygame.font.Font(None,24).render(str(ordre.index(i)+1),True,(45,70,47))
                poner(s,im,(x,99))
        if paso==2 and actuel>=0: pinza(s,(45+ordre[actuel]*72,80),t%.85>.3)
    elif juego==3:
        x=120+math.sin(t*1.6)*65 if paso==0 else 120
        y=65+math.cos(t*1.6)*17 if paso==0 else 78
        if paso==2: x=mezclar(120,192,min(1,t/1.5))
        poner(s,sprite('canasta',90,65),(x,y))
        if paso>0:
            yy=mezclar(-20,115,t/2.8)
            if paso==2 or yy<70: poner(s,sprite('bomba' if paso==2 else 'dulce',37,37),(120,yy))
            if paso==1 and yy>=70:
                poner(s,sprite('estrella',28,28),(120,59))
    else:
        centre=(120,57);r=39
        pts=[(120+r*math.sin(i*math.tau/60),57-r*math.cos(i*math.tau/60)) for i in range(61)]
        pygame.draw.lines(s,(99,127,100),False,pts,2)
        n=max(1,min(61,int(t/3*61)))
        if paso==0:
            poner(s,magia('joya',28),pts[0]);pinza(s,(mezclar(185,120,t/2),mezclar(80,18,t/2)),t>2)
        else:
            if n>1: pygame.draw.lines(s,(180,121,43),False,pts[:n],5)
            poner(s,magia('pluma',40),pts[n-1])
            if paso==2: poner(s,magia('espiritu',52),(120,57-max(0,t-2)*30))
