"""Mano de perfil: índice arriba, pulgar abajo y dedos recogidos en la palma."""
import pygame
import pygame.gfxdraw
from pathlib import Path
from functools import lru_cache


@lru_cache(maxsize=12)
def mano_ilustrada(cerrada,lado):
    ruta=Path(__file__).parent/'assets'/'mano-pinza-v2.png'
    if not ruta.exists():return None
    atlas=pygame.image.load(str(ruta)).convert_alpha()
    w,h=atlas.get_size();mitad=w//2
    partes=[atlas.subsurface((i*mitad,0,mitad,h)).copy() for i in (0,1)]
    limites=partes[0].get_bounding_rect(min_alpha=20).union(partes[1].get_bounding_rect(min_alpha=20))
    imagen=partes[int(cerrada)].subsurface(limites).copy()
    return pygame.transform.smoothscale(imagen,(lado,round(imagen.get_height()*lado/imagen.get_width())))


def mano_lateral(s,centro,cierre=0,lado=72):
    cierre=max(0,min(1,cierre))
    imagen=mano_ilustrada(cierre>=.5,round(lado))
    if imagen is not None:
        s.blit(imagen,imagen.get_rect(center=tuple(map(round,centro))))
        return
    capa=pygame.Surface((300,260),pygame.SRCALPHA)
    tinta=(98,69,46);piel=(244,207,159);luz=(255,231,191)
    # La punta del pulgar asciende hacia el índice, sin mover la palma.
    yy=154-81*cierre
    contorno=[(31,122),(62,115),(86,91),(105,62),(129,43),(159,39),
              (203,45),(249,57),(259,64),(257,75),(248,81),(203,76),
              (164,70),(148,76),(133,99),(143,121),(166,135),
              (191,yy+7),(226,yy-5),(245,yy-3),(252,yy+7),
              (246,yy+18),(222,yy+28),(195,yy+41),(168,194),
              (143,213),(107,216),(80,202),(53,198),(31,202)]
    pygame.gfxdraw.filled_polygon(capa,contorno,piel)
    pygame.gfxdraw.aapolygon(capa,contorno,tinta)
    pygame.draw.lines(capa,tinta,False,contorno+[contorno[0]],4)
    # Trois doigts repliés et pli de paume donnent la silhouette d'une main.
    for x,y in ((108,128),(100,151),(94,174)):
        pygame.draw.arc(capa,tinta,(x,y,54,32),-.8,2.4,3)
    pygame.draw.arc(capa,(183,130,89),(75,165,75,43),.1,1.9,3)
    pygame.draw.line(capa,luz,(157,49),(213,56),5)
    pygame.draw.ellipse(capa,luz,(227,61,20,10))
    pygame.draw.ellipse(capa,luz,(227,yy+3,17,10))
    # Manche de tissu, qui rend le poignet identifiable même en petit.
    pygame.draw.rect(capa,(107,137,101),(10,119,44,89),border_radius=6)
    pygame.draw.line(capa,(205,218,175),(46,125),(46,201),4)
    taille=(round(lado),round(lado*260/300))
    capa=pygame.transform.smoothscale(capa,taille)
    s.blit(capa,capa.get_rect(center=tuple(map(round,centro))))
