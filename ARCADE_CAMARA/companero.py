"""Reacciones del familiar y señales de control fuera del área de juego."""
import math
import pygame
from interfaz import papel, escribir, PAPEL, MUSGO
from diario import estrella
from gestos import mano_lateral


class Companero:
    def __init__(self):
        self.emocion='curioso'
        self.resta=0
        self.t=0

    def actualizar(self,dt,eventos=()):
        self.t+=dt
        self.resta=max(0,self.resta-dt)
        if not self.resta: self.emocion='curioso'
        for tipo,*_ in eventos:
            emocion={'captura':'contento','entrega':'festejo','picadura':'sorpresa','escape':'triste','explosion':'sorpresa','veneno':'sorpresa','magia':'festejo','combo':'festejo'}.get(tipo)
            if emocion: self.emocion=emocion;self.resta=1.5

    def postura(self,pos,objetivo=None):
        x,y=pos
        angulo=0
        if objetivo: angulo=max(-8,min(8,(x-objetivo[0])*.05))
        if self.emocion=='festejo': y-=abs(math.sin(self.t*12))*11;angulo=math.sin(self.t*13)*12
        elif self.emocion=='sorpresa': angulo=math.sin(self.t*35)*8
        elif self.emocion=='triste': angulo=-10
        return (x,y),angulo

    def dibujar(self,s,pos):
        x,y=pos
        if self.emocion=='festejo':
            for i in range(5):
                a=self.t*2+i*math.tau/5
                estrella(s,(x+math.cos(a)*62,y+math.sin(a)*62),7,(226,181,75))
        elif self.emocion=='contento':
            for dx in (-40,40):
                pygame.draw.circle(s,(210,126,110),(round(x+dx),round(y-35)),6)
        elif self.emocion in ('sorpresa','triste'):
            papel(s,(x-38,y-80,76,30))
            escribir(s,'¡Ay!' if self.emocion=='sorpresa' else 'Ups…',(x,y-65),20,negrita=True)


def guia(s,pos,cerrada,juego,carga,control=None,raton=False):
    """El margen lateral no tapa bichos, faroles ni trazos."""
    papel(s,(10,205,140,225))
    escribir(s,'TU MANO',(80,229),17,negrita=True)
    perdida=pos is None
    borde=not raton and control is not None and getattr(control,'cerca_borde',False)
    color=(161,91,55) if borde or perdida else MUSGO
    pygame.draw.circle(s,color,(80,280),31)
    mano_lateral(s,(80,280),float(cerrada),72)
    texto='Buscando…' if perdida else ('Con bichito' if carga else ('Cerrada' if cerrada else 'Abierta'))
    escribir(s,texto,(80,329),18,negrita=True,ancho=125)
    lineas=('Volvé al','centro') if borde else (('Mostrá la','mano completa') if perdida else (('Mové en','cada dirección') if juego==3 else (('Mantené y','soltá en bolsa') if carga else ('Pinza para','interactuar'))))
    for i,linea in enumerate(lineas): escribir(s,linea,(80,363+i*24),16,ancho=125)
