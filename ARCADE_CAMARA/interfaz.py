"""Papel, tinta y carteles de juego con jerarquía y texto legible."""
import math
from functools import lru_cache
import pygame
from pathlib import Path
from identidad import fuente

PAPEL=(247,238,211)
TINTA=(39,64,46)
MUSGO=(59,83,59)
BORDE=(157,153,112)


@lru_cache(maxsize=32)
def lectura(tam,negrita=False):
    ruta=Path('C:/Windows/Fonts')/('Candarab.ttf' if negrita else 'Candara.ttf')
    return pygame.font.Font(str(ruta) if ruta.exists() else pygame.font.match_font('segoeui',bold=negrita),tam)


@lru_cache(maxsize=64)
def tipografia(n,negrita,titulo):
    ruta=Path('C:/Windows/Fonts/Gabriola.ttf')
    return pygame.font.Font(str(ruta),round(n*1.5)) if titulo and ruta.exists() else lectura(n,negrita)


@lru_cache(maxsize=512)
def texto_renderizado(texto,tam,color,negrita,ancho,titulo):
    def elegir(n):return tipografia(n,negrita,titulo)
    f=elegir(tam)
    if ancho:
        while f.size(texto)[0]>ancho and tam>16:
            tam-=1;f=elegir(tam)
    imagen=f.render(texto,True,color)
    if titulo:
        imagen=imagen.subsurface(imagen.get_bounding_rect()).copy()
    return imagen


def escribir(s,texto,centro,tam=20,color=TINTA,negrita=False,ancho=None,titulo=False):
    imagen=texto_renderizado(texto,tam,tuple(color),negrita,ancho,titulo)
    s.blit(imagen,imagen.get_rect(center=centro))


def limpiar_cache():
    texto_renderizado.cache_clear()
    tipografia.cache_clear()
    lectura.cache_clear()


def papel(s,rect,color=PAPEL):
    rect=pygame.Rect(rect)
    oscuro=sum(color)<350
    pygame.draw.rect(s,(23,40,32),rect.move(0,4),border_radius=4)
    pygame.draw.rect(s,color,rect,border_radius=4)
    pygame.draw.rect(s,(115,139,103) if oscuro else (188,170,123),rect,1,border_radius=4)
    # Fibras suaves y costura: materiales compartidos en toda la interfaz.
    if not oscuro:
        for yy in range(rect.top+8,rect.bottom-5,7):
            xx=rect.left+7+(yy*13)%max(1,rect.width-20)
            pygame.draw.line(s,(235,224,196),(xx,yy),(min(xx+13,rect.right-6),yy))
    borde=(168,185,133) if oscuro else (208,193,153)
    if rect.height>=55:
        pygame.draw.line(s,borde,(rect.left+9,rect.top+9),(rect.right-9,rect.top+9))
        pygame.draw.line(s,borde,(rect.left+9,rect.bottom-9),(rect.right-9,rect.bottom-9))
    if rect.width>700 and rect.height>300:
        pygame.draw.line(s,(193,174,129),(rect.left+19,rect.top+22),(rect.left+19,rect.bottom-22),2)
        for yy in range(rect.top+40,rect.bottom-20,38):
            pygame.draw.line(s,(121,123,88),(rect.left-4,yy),(rect.left+24,yy-3),3)


def boton(s,rect,label,activo=False):
    rect=pygame.Rect(rect)
    color=(83,113,79) if activo else MUSGO
    pygame.draw.polygon(s,(25,43,33),[(rect.left-7,rect.top+7),(rect.right+7,rect.top+7),(rect.right-2,rect.centery+4),(rect.right+7,rect.bottom+5),(rect.left-7,rect.bottom+5),(rect.left+2,rect.centery+4)])
    pygame.draw.polygon(s,color,[(rect.left-7,rect.top),(rect.right+7,rect.top),(rect.right-2,rect.centery),(rect.right+7,rect.bottom),(rect.left-7,rect.bottom),(rect.left+2,rect.centery)])
    for yy in (rect.top+6,rect.bottom-6):
        for xx in range(rect.left+10,rect.right-8,9): pygame.draw.line(s,(166,183,132),(xx,yy),(xx+4,yy))
    escribir(s,label,rect.center,27,PAPEL,ancho=rect.width-32,titulo=True)


def foco_control(s, rect, puntero, activar, ahora):
    """Marca el control señalado y confirma la pinza o el clic."""
    if puntero is None or not rect.collidepoint(puntero):
        return
    marco = rect.inflate(18, 8)
    pygame.draw.rect(s, TINTA, marco.inflate(4, 4), 3, border_radius=8)
    pygame.draw.rect(s, (255, 233, 166), marco, 3 if activar else 2, border_radius=7)
    brillo = round(3 + (1 + math.sin(ahora * 5)) * 1.5)
    for x in (marco.left, marco.right):
        y = marco.centery
        pygame.draw.polygon(s, (255, 233, 166),
                            [(x, y-brillo), (x+brillo, y), (x, y+brillo), (x-brillo, y)])


def separador(s,x,y,ancho=160):
    pygame.draw.line(s,BORDE,(x-ancho//2,y),(x-15,y))
    pygame.draw.line(s,BORDE,(x+15,y),(x+ancho//2,y))
    hojita(s,x,y)


def hojita(s,x,y,color=(124,149,92)):
    pygame.draw.line(s,color,(x-9,y+6),(x+11,y-7),2)
    pygame.draw.ellipse(s,color,(x-7,y-8,11,6))
    pygame.draw.ellipse(s,color,(x+1,y-1,11,6))


def cabecera(s,numero,titulo,subtitulo,etiqueta,puntos,meta,tiempo):
    papel(s,(16,6,928,86))
    pygame.draw.polygon(s,MUSGO,[(30,6),(78,6),(78,77),(54,65),(30,77)])
    escribir(s,f'{numero:02d}',(54,34),26,PAPEL,True)
    escribir(s,titulo,(243,35),32,titulo=True,ancho=300)
    escribir(s,subtitulo.capitalize(),(243,68),16,ancho=305)
    for xx in (409,724): pygame.draw.line(s,BORDE,(xx,23),(xx,75))
    escribir(s,etiqueta.capitalize(),(565,25),17)
    escribir(s,f'{puntos} / {meta}',(565,53),30,titulo=True)
    for i in range(min(meta,12)):
        xx=565+(i-(min(meta,12)-1)/2)*15
        pygame.draw.circle(s,MUSGO if i<round(puntos/meta*min(meta,12)) else (204,197,167),(round(xx),78),3)
    color=(147,53,58) if tiempo<15 else TINTA
    pygame.draw.circle(s,color,(759,46),16,2)
    pygame.draw.line(s,color,(759,46),(759,34),2)
    pygame.draw.line(s,color,(759,46),(767,51),2)
    escribir(s,'Tiempo restante',(853,26),16,color)
    escribir(s,f'{math.ceil(tiempo):02d} s',(853,61),35,color,titulo=True)


def aviso(s,titulo,detalle='',y=104):
    papel(s,(178,y,604,60))
    escribir(s,titulo,(480,y+18),26,titulo=True,ancho=570)
    if detalle:escribir(s,detalle,(480,y+44),18,ancho=570)


def pie(s,mensaje,ayuda='',borrar=False,compacto=False):
    y=647 if compacto else 625
    alto=71 if compacto else 93
    papel(s,(16,y,928,alto))
    escribir(s,mensaje,(480,y+20),26,titulo=True,ancho=880)
    if ayuda and not compacto:
        escribir(s,ayuda,(480,y+46),19,ancho=880)
    controles=[('P','Pausa'),('M','Audio'),('C','Cámara'),('F11','Pantalla'),('Esc','Inicio')]
    if borrar:controles.insert(0,('R','Borrar'))
    paso=140 if borrar else 160
    primero=480-(len(controles)-1)*paso/2
    yy=702
    for i,(tecla,accion) in enumerate(controles):
        x=primero+i*paso
        ancho=32 if len(tecla)<2 else 42
        pygame.draw.rect(s,MUSGO,(x-64,yy-11,ancho,23),border_radius=5)
        escribir(s,tecla,(x-64+ancho/2,yy),14,PAPEL,True)
        escribir(s,accion,(x+19,yy),16)
