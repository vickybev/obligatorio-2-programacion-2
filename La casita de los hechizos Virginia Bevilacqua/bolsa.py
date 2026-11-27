"""Bolsa de tela ilustrada, con la abertura en las coordenadas de entrega."""
from functools import lru_cache
from pathlib import Path
import math
import pygame
from juego import NIDO


@lru_cache(maxsize=1)
def ilustracion():
    ruta=Path(__file__).parent/'assets'/'bolsa-bosque-v1.png'
    if not ruta.exists():
        return None
    imagen=pygame.image.load(str(ruta)).convert_alpha()
    imagen=imagen.subsurface(imagen.get_bounding_rect(min_alpha=12)).copy()
    return pygame.transform.smoothscale(imagen,(260,210))


def dibujar(pantalla,activa,ahora):
    imagen=ilustracion()
    if imagen is None:
        return False
    x,y=NIDO
    sombra=pygame.Surface((280,40),pygame.SRCALPHA)
    pygame.draw.ellipse(sombra,(10,20,16,95),(14,5,252,24))
    pantalla.blit(sombra,(x-140,y+104))
    pantalla.blit(imagen,(x-130,y-80))
    if activa:
        brillo=pygame.Surface((200,142),pygame.SRCALPHA)
        intensidad=int(125+35*math.sin(ahora*4))
        pygame.draw.ellipse(brillo,(255,224,157,intensidad),(15,15,170,112),3)
        pantalla.blit(brillo,(x-100,y-71))
    return True


def labio_delantero(pantalla):
    imagen=ilustracion()
    if imagen is not None:
        # Volver a pintar la parte frontal hace que los bichitos queden adentro.
        pantalla.blit(imagen,(NIDO[0]-130,NIDO[1]+28),(0,108,260,102))
