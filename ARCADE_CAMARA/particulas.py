"""Reacciones visuales compartidas, con tiempo de vida y cantidad acotada."""
import math
import random
import pygame


class Particulas:
    def __init__(self):
        self.elementos=[]
        self.ondas=[]
        self.cartel=''
        self.aviso=0
        self.capa=pygame.Surface((960,720),pygame.SRCALPHA)

    def recibir(self,eventos,juego):
        for tipo,pos,numero in eventos:
            if tipo=='polvo':
                cantidad=2;color=(255,218,166);vida=.7
            elif tipo in ('picadura','explosion','veneno'):
                cantidad=32 if tipo=='explosion' else 20
                color=(181,118,224);vida=.9
                self.cartel={'explosion':'¡PUF! EXPLOSIÓN','veneno':'¡VENENO!','picadura':'¡AY!'}[tipo]
                self.aviso=1.1
            elif tipo in ('magia','combo'):
                cantidad=30;color=(255,217,133);vida=1.1
                self.cartel='¡IMÁN ACTIVADO!' if tipo=='magia' else f'¡COMBO x{numero}!'
                self.aviso=1.3
            elif tipo=='entrega':
                cantidad=35;color=(255,173,211);vida=1.1
                self.cartel={1:'¡A LA BOLSA!',2:'¡CONSTELACIÓN COMPLETA!',4:'¡SELLO LIBERADO!'}[juego] if juego!=3 else '¡MAGIA!'
                self.aviso=1.0
            elif tipo=='captura':
                cantidad=9;color=(255,232,173);vida=.55
            else:
                continue
            if tipo!='polvo':
                self.ondas.append(dict(pos=pos,t=0,vida=.6,color=color))
            for _ in range(cantidad):
                a=random.random()*math.tau
                v=random.uniform(10,45) if tipo=='polvo' else random.uniform(30,135)
                self.elementos.append(dict(x=pos[0],y=pos[1],vx=math.cos(a)*v,
                    vy=math.sin(a)*v-20,t=0,vida=vida*random.uniform(.7,1.15),
                    color=color,r=random.uniform(2,5),humo=tipo in ('explosion','veneno')))
            self.elementos=self.elementos[-360:]
            self.ondas=self.ondas[-20:]

    def actualizar(self,dt):
        self.aviso=max(0,self.aviso-dt)
        for p in self.elementos:
            p['t']+=dt;p['x']+=p['vx']*dt;p['y']+=p['vy']*dt
            p['vy']+=dt*26
        self.elementos=[p for p in self.elementos if p['t']<p['vida']]
        for o in self.ondas:o['t']+=dt
        self.ondas=[o for o in self.ondas if o['t']<o['vida']]

    def dibujar(self,pantalla,fuentes):
        self.capa.fill((0,0,0,0))
        for o in self.ondas:
            t=o['t']/o['vida'];color=(*o['color'],int((1-t)*150))
            pygame.draw.circle(self.capa,color,tuple(map(round,o['pos'])),int(15+t*60),2)
        for p in self.elementos:
            t=p['t']/p['vida'];alpha=int(220*(1-t));x,y=p['x'],p['y']
            if p['humo']:
                pygame.draw.circle(self.capa,(*p['color'],int(alpha*.5)),(round(x),round(y)),int(p['r']*2+t*12))
            else:
                r=p['r']*(1-t*.4)
                puntos=[(x+math.cos(i*math.pi/4)*r*(1 if i%2==0 else .27),
                         y+math.sin(i*math.pi/4)*r*(1 if i%2==0 else .27)) for i in range(8)]
                pygame.draw.polygon(self.capa,(*p['color'],alpha),puntos)
        pantalla.blit(self.capa,(0,0))
        if self.aviso>0:
            imagen=fuentes[22].render(self.cartel,True,(255,229,181))
            rect=imagen.get_rect(center=(480,104))
            pygame.draw.rect(pantalla,(48,29,60),rect.inflate(24,8),border_radius=10)
            pantalla.blit(imagen,rect)
