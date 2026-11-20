"""Movimiento ambiental suave, separado de las reglas de cada juego."""
import math
import random
import pygame


class Ambiente:
    def __init__(self,imagen):
        self.imagen=imagen
        self.t=0.0
        self.variantes={}
        rng=random.Random(42)

        self.particulas=[(rng.randrange(960),rng.randrange(720),rng.uniform(.5,1.4),rng.random()*math.tau) for _ in range(19)]

    def actualizar(self,dt):
        self.t+=dt

    def dibujar(self,pantalla):
        # Pequeño vaivén de cámara: el fondo se desplaza sin mover las colisiones.
        vw,vh=pantalla.get_size()
        iw,ih=self.imagen.get_size()
        factor=max(vw/iw,vh/ih)*1.015
        ancho=round(iw*factor)+round(math.sin(self.t*.14)*3)
        alto=round(ancho*ih/iw)
        clave=(vw,vh,ancho)
        if clave not in self.variantes:
            self.variantes[clave]=pygame.transform.smoothscale(self.imagen,(ancho,alto))
        x=(vw-ancho)//2+round(math.sin(self.t*.19)*3)
        y=(vh-alto)//2+round(math.cos(self.t*.16)*2)
        pantalla.blit(self.variantes[clave],(x,y))
        for i,(px,py,vel,fase) in enumerate(self.particulas):
            if i%3:
                xx=(px*vw/960+self.t*8*vel+math.sin(self.t*.6+fase)*14)%vw
                yy=(py+self.t*12*vel)%720
                dibujo=pygame.Surface((18,18),pygame.SRCALPHA)
                pygame.draw.ellipse(dibujo,(198,189,125,145),(4,5,10,5))
                dibujo=pygame.transform.rotate(dibujo,math.sin(self.t+fase)*35)
            else:
                xx=(px*vw/960+math.sin(self.t*.35+fase)*28)%vw
                yy=(py+math.sin(self.t*.5+fase)*22)%720
                dibujo=pygame.Surface((24,24),pygame.SRCALPHA)
                intensidad=int(45+35*math.sin(self.t*1.2+fase))
                pygame.draw.circle(dibujo,(250,217,155,intensidad),(12,12),9)
                pygame.draw.circle(dibujo,(255,237,181,intensidad+70),(12,12),2)
            pantalla.blit(dibujo,dibujo.get_rect(center=(round(xx),round(yy))))

