"""Animaciones de picadura y entregas. No modifican puntos ni controles."""
import math
import pygame
from juego import NIDO
from bolsa import dibujar as dibujar_bolsa, labio_delantero


class Efectos:
    def __init__(self):
        self.golpe = 0.0
        self.caidas = []
        self.guardados = 0

    def recibir(self, eventos):
        for tipo, pos, numero in eventos:
            if tipo == 'picadura':
                self.golpe = 0.85
            elif tipo == 'entrega':
                self.caidas.append({'desde': pos, 'numero': numero, 't': 0.0})

    def actualizar(self, dt):
        self.golpe = max(0, self.golpe-dt)
        for caida in self.caidas:
            caida['t'] += dt
            if caida['t'] >= 0.7:
                self.guardados = max(self.guardados, caida['numero'])
        self.caidas = [c for c in self.caidas if c['t'] < 0.7]

    @staticmethod
    def casilla(numero):
        return (NIDO[0]-48+((numero-1)%4)*32,
                NIDO[1]+12-((numero-1)//4)*27)

    def bolsa(self, pantalla, activa, ahora, bicho):
        x,y = NIDO
        ilustrada=dibujar_bolsa(pantalla,activa,ahora)
        if not ilustrada:
            tinta=(25,16,37)
            pygame.draw.ellipse(pantalla,(19,17,30),(x-102,y+65,204,25))
            cuerpo=[(x-73,y-30),(x-94,y+42),(x-78,y+77),
                    (x+77,y+77),(x+94,y+42),(x+73,y-30)]
            pygame.draw.polygon(pantalla,tinta,cuerpo)
            pygame.draw.polygon(pantalla,(126,80,120),cuerpo,5)
        # Interior visible: cada entrega conserva su propio bichito.
        for numero in range(1,self.guardados+1):
            px,py=self.casilla(numero)
            bicho(pantalla,(px,py+math.sin(ahora*2+numero)*1.5),False,ahora+numero,.56)
        for caida in self.caidas:
            t=caida['t']/0.7
            sx,sy=caida['desde']; ex,ey=self.casilla(caida['numero'])
            px=sx+(ex-sx)*t
            py=sy+(ey-sy)*t-85*math.sin(t*math.pi)
            bicho(pantalla,(px,py),False,ahora*5,1-.44*t)
        if ilustrada:
            labio_delantero(pantalla)
        else:
            # Boca y costura: mantiene la misma elipse de entrega de las reglas.
            pygame.draw.ellipse(pantalla,(244,129,176) if activa else (192,152,196),(x-85,y-56,170,112),5)
            pygame.draw.arc(pantalla,(225,174,194),(x-90,y-46,180,112),math.pi,math.tau,3)
            for lado in (-1,1):
                xx=x+lado*89
                pygame.draw.line(pantalla,(224,179,145),(xx,y),(xx+lado*14,y+25),4)
                pygame.draw.circle(pantalla,(244,129,176),(xx+lado*14,y+28),6)

    def dibujar_picadura(self, pantalla, pos, ahora, fuentes):
        if not self.golpe or pos is None:
            return
        x,y=pos
        # Trazo de rayo con núcleo claro, sin destello de pantalla completa.
        if self.golpe > 0.3:
            cima=max(105,y-170)
            puntos=[(x+8,cima),(x-16,cima+40),(x+10,cima+37),
                    (x-13,y-55),(x+15,y-70),(x,y-18)]
            pygame.draw.lines(pantalla,(179,106,246),False,puntos,12)
            pygame.draw.lines(pantalla,(255,237,173),False,puntos,4)
        for dx in (-17,12):
            cx=x+dx;cy=y+5
            pygame.draw.line(pantalla,(50,18,65),(cx-7,cy-6),(cx+7,cy+6),4)
            pygame.draw.line(pantalla,(50,18,65),(cx-7,cy+6),(cx+7,cy-6),4)
        for j in range(5):
            a=j*math.tau/5+ahora*4
            pygame.draw.circle(pantalla,(244,185,243),
                               (int(x+math.cos(a)*51),int(y+math.sin(a)*44)),3)
        imagen=fuentes[28].render('¡AY!  -4 s',True,(255,206,157))
        pantalla.blit(imagen,imagen.get_rect(center=(x,max(116,y-100))))
