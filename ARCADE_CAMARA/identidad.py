"""Nombre, lettering ilustrado y tipografía de lectura de la casita."""
from pathlib import Path
import pygame

NOMBRE='La casita de los hechizos'


def fuente(tamano,negrita=False):
    ruta=pygame.font.match_font('constantia',bold=negrita)
    return pygame.font.Font(ruta,tamano)


class Identidad:
    def __init__(self):
        self.logo=None
        ruta=Path(__file__).parent/'assets'/'logo-casita-v1.png'
        if ruta.exists():
            imagen=pygame.image.load(str(ruta)).convert_alpha()
            imagen=imagen.subsurface(imagen.get_bounding_rect(min_alpha=10)).copy()
            escala=min(590/imagen.get_width(),139/imagen.get_height())
            self.logo=pygame.transform.smoothscale(imagen,(round(imagen.get_width()*escala),round(imagen.get_height()*escala)))
        self.lectura=pygame.font.Font(str(Path('C:/Windows/Fonts/Candara.ttf')),22)

    def dibujar(self,pantalla):
        if self.logo is not None:
            pantalla.blit(self.logo,self.logo.get_rect(center=(640,83)))
        else:
            texto=fuente(38,True).render(NOMBRE,True,(43,66,48))
            pantalla.blit(texto,texto.get_rect(center=(640,82)))
        texto=self.lectura.render('Cuatro pequeñas aventuras. Un poquito de magia en tus manos.',True,(58,79,53))
        pantalla.blit(texto,texto.get_rect(center=(640,175)))
