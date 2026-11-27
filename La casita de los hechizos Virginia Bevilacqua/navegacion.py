"""Regreso al inicio con cierre de pinza, sin teclado."""
import pygame
from interfaz import papel, escribir, MUSGO, PAPEL


class Regreso:
    def __init__(self):
        self.rect=pygame.Rect(822,108,122,49)
        self.permanencia=0
        self.estado=None
        self.anterior=False

    def actualizar(self,dt,estado,pos,cerrada,click=False):
        pinza=cerrada and not self.anterior
        self.anterior=cerrada
        dentro=pos is not None and self.rect.collidepoint(pos)
        return estado!='menu' and dentro and (click or pinza)

    def dibujar(self,s):
        papel(s,self.rect,MUSGO)
        x,y=self.rect.topleft
        # Icono de casita y etiqueta breve.
        pygame.draw.lines(s,PAPEL,False,[(x+12,y+24),(x+23,y+14),(x+34,y+24)],2)
        pygame.draw.rect(s,PAPEL,(x+16,y+24,15,12),2)
        escribir(s,'Inicio',(x+79,y+24),22,PAPEL,titulo=True,ancho=70)
        if self.permanencia:
            pygame.draw.rect(s,(234,204,127),(x+7,y+43,round(108*min(1,self.permanencia/1.2)),3))
