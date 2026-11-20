"""Elementos ilustrados del juego de dibujo: marco, espíritu, pluma y joya."""
from functools import lru_cache
from pathlib import Path
import pygame


@lru_cache(maxsize=1)
def lamina():
    ruta=Path(__file__).parent/'assets'/'sellos-bosque-v2.png'
    return pygame.image.load(str(ruta)).convert_alpha() if ruta.exists() else None


@lru_cache(maxsize=12)
def sprite(nombre,lado):
    imagen=lamina()
    if imagen is None:
        return None
    columna,fila={'marco':(0,0),'espiritu':(1,0),'pluma':(0,1),'joya':(1,1)}[nombre]
    w,h=imagen.get_size()
    x0,x1=round(columna*w/2),round((columna+1)*w/2)
    y0,y1=round(fila*h/2),round((fila+1)*h/2)
    celda=imagen.subsurface((x0,y0,x1-x0,y1-y0)).copy()
    celda=celda.subsurface(celda.get_bounding_rect(min_alpha=12)).copy()
    escala=lado/max(celda.get_size())
    return pygame.transform.smoothscale(celda,(max(1,round(celda.get_width()*escala)),max(1,round(celda.get_height()*escala))))


def cursor(pantalla,pos,cerrada,ahora):
    x,y=map(round,pos)
    pygame.draw.circle(pantalla,(233,192,111) if cerrada else (247,239,210),(x,y),7,2)
    imagen=sprite('pluma',65)
    if imagen is not None:
        pantalla.blit(imagen,(x-5,y-imagen.get_height()+5))
