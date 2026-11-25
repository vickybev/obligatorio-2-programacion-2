"""Sprites ilustrados: prepara las variantes una vez y anima al dibujar."""
import math
from functools import lru_cache
from pathlib import Path

import pygame
from armario import dibujar_prenda

ASSETS = Path(__file__).parent / 'assets'


@lru_cache(maxsize=3)
def original(nombre):
    ruta = ASSETS / f'{nombre}-anime-v1.png'
    if not ruta.exists():
        return None
    imagen = pygame.image.load(str(ruta)).convert_alpha()
    # Elimina solamente margen transparente, sin tocar la ilustración.
    return imagen.subsurface(imagen.get_bounding_rect()).copy()


@lru_cache(maxsize=256)
def variante(nombre, lado, fase):
    imagen = original(nombre)
    if imagen is None:
        return None
    proporcion = lado / max(imagen.get_size())
    w,h = imagen.get_size()
    if nombre != 'familiar':
        a = fase*math.tau/16
        ancho = max(1,round(w*proporcion*(.93+.07*math.cos(a))))
        imagen = pygame.transform.smoothscale(imagen,(ancho,max(1,round(h*proporcion))))
        return pygame.transform.rotate(imagen,math.sin(a)*5)
    return pygame.transform.smoothscale(imagen,(max(1,round(w*proporcion)),max(1,round(h*proporcion))))


def dibujar_bicho(pantalla, pos, malo, tiempo, escala):
    nombre = 'violeta' if malo else 'polilla'
    fase = int(tiempo*5)%16
    imagen = variante(nombre,max(12,round(57*escala)),fase)
    if imagen is None:
        return False
    x,y = pos
    y += math.sin(tiempo*2)*1.5*escala
    pantalla.blit(imagen,imagen.get_rect(center=(round(x),round(y))))
    return True


def dibujar_familiar(pantalla, pos, cerrada, tiempo, angulo=0, prenda=None):
    imagen = variante('familiar',102,0)
    if imagen is None:
        return False
    capa=pygame.Surface((144,144),pygame.SRCALPHA)
    x,y=72,72
    capa.blit(imagen,imagen.get_rect(center=(x,y)))
    # La boca responde al gesto en la misma posición que el cursor real.
    if not cerrada:
        pygame.draw.ellipse(capa,(249,230,203),(x-15,y+7,28,19))
        pygame.draw.ellipse(capa,(33,15,38),(x-12,y+8,24,20))
        pygame.draw.ellipse(capa,(225,105,153),(x-7,y+19,14,7))
        for dx in (-6,6):
            pygame.draw.polygon(capa,(255,243,217),[(x+dx-3,y+10),(x+dx+3,y+10),(x+dx,y+15)])
    if prenda is not None:
        dibujar_prenda(capa, prenda)
    if angulo: capa=pygame.transform.rotate(capa,angulo)
    pantalla.blit(capa,capa.get_rect(center=tuple(map(round,pos))))
    return True
