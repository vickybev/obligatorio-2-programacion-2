"""Lee seis ilustraciones desde una lámina de sprites con celdas iguales."""
from functools import lru_cache
from pathlib import Path
import pygame

NOMBRES={'farol':(0,0),'dulce':(1,0),'pocion':(2,0),
         'bomba':(0,1),'estrella':(1,1),'canasta':(2,1)}


@lru_cache(maxsize=1)
def lamina():
    ruta=Path(__file__).parent/'assets'/'objetos-bosque-v2.png'
    return pygame.image.load(str(ruta)).convert_alpha() if ruta.exists() else None


@lru_cache(maxsize=40)
def sprite(nombre,ancho,alto,apagado=False):
    atlas=lamina()
    if atlas is None:
        return None
    columna,fila=NOMBRES[nombre]
    w,h=atlas.get_size()
    x0,x1=round(columna*w/3),round((columna+1)*w/3)
    y0,y1=round(fila*h/2),round((fila+1)*h/2)
    imagen=atlas.subsurface((x0,y0,x1-x0,y1-y0)).copy()
    imagen=imagen.subsurface(imagen.get_bounding_rect(min_alpha=12)).copy()
    proporcion=min(ancho/imagen.get_width(),alto/imagen.get_height())
    imagen=pygame.transform.smoothscale(imagen,(max(1,round(imagen.get_width()*proporcion)),max(1,round(imagen.get_height()*proporcion))))
    if apagado:
        imagen.fill((142,157,139,255),special_flags=pygame.BLEND_RGBA_MULT)
    return imagen
