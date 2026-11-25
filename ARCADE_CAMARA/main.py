"""La casita de los hechizos: cuatro minijuegos por cámara en 16:9."""
import argparse
import math
import random
import sys
from pathlib import Path

import pygame

from juego import NIDO, REFUGIO_LUNA, Partida
from vision import abrir_camara, redimensionar
from ajustes import ALTO, ANCHO, FPS, FONDO, CREMA, LIMA, CORAL, VIOLETA, NIVELES_AVENTURAS
from efectos import Efectos
from sonido import Sonido
from particulas import Particulas
from cartas import Carrusel as Coleccion, cursor as cursor_cartas
from identidad import Identidad, NOMBRE, fuente
from interfaz import cabecera, pie as panel_pie, papel as panel_papel, escribir, lectura, MUSGO, boton, separador, TINTA, PAPEL
from faroles import Faroles, cursor as cursor_faroles
from banquete import Banquete
from sellos import Sellos
from arte_sellos import cursor as cursor_sellos
from objetos_anime import sprite
from ambiente import Ambiente
from personajes import dibujar_bicho, dibujar_familiar
from tutorial_animado import dibujar as animar_tutorial
from navegacion import Regreso
from interfaz import limpiar_cache
from diario import Diario, REPETIR, VOLVER, DIARIO_MENU, recuerdo
from companero import Companero, guia as guia_gesto
from gestos import mano_lateral



def texto(pantalla, fuentes, contenido, pos, tam=24, color=CREMA, centro=False):
    """Dibuja un texto con la tipografía y alineación de la pantalla activa."""
    if tam>=34 and centro:
        escribir(pantalla,contenido,pos,tam,color,titulo=True,ancho=pantalla.get_width()-80)
        return
    imagen = fuentes[tam].render(contenido, True, color)
    rect = imagen.get_rect()
    if centro:
        rect.center = pos
    else:
        rect.topleft = pos
    pantalla.blit(imagen, rect)


def bicho(pantalla, pos, malo, fase, escala=1):
    """Dibuja un bicho con la variante visual que corresponde a su tipo."""
    if dibujar_bicho(pantalla,pos,malo,fase,escala):
        return
    x, y = int(pos[0]), int(pos[1])
    r = int(18*escala)
    color = VIOLETA if malo else (255, 205, 99)
    pygame.draw.ellipse(pantalla, (7, 17, 23), (x-r,y+r-1,r*2,8))
    for lado in (-1,1):
        for i in range(3):
            yy = y-r//2+i*r//2
            punta = (x+lado*(r+9),yy+int(math.sin(fase+i)*5))
            pygame.draw.line(pantalla,color,(x+lado*r//2,yy),punta,3)
    pygame.draw.circle(pantalla,(15,12,28),(x,y),r+3)
    pygame.draw.circle(pantalla,color,(x,y),r)
    if malo:
        for lado in (-1,1):
            pygame.draw.polygon(pantalla,color,[(x+lado*8,y-r+4),(x+lado*19,y-r-11),(x+lado*15,y-r+10)])
    for dx in (-6,6):
        pygame.draw.circle(pantalla,CREMA,(x+dx,y-4),6)
        pygame.draw.ellipse(pantalla,FONDO,(x+dx-3,y-8,6,10))
        pygame.draw.circle(pantalla,CREMA,(x+dx-1,y-6),2)
    for dx in (-11,11):
        pygame.draw.line(pantalla,(226,118,149),(x+dx-2,y+5),(x+dx+2,y+5),2)
    pygame.draw.arc(pantalla,FONDO,(x-6,y+1,12,9),0,math.pi,2)


def monstruo(pantalla, pos, cerrada, segundos, carga=None, angulo=0):
    """Dibuja la criatura que acompaña al cursor durante la captura."""
    if dibujar_familiar(pantalla,pos,cerrada,segundos,angulo):
        if carga:
            x,y = pos
            bicho(pantalla,(x+31,y+26),False,segundos*5,.55)
            pygame.draw.arc(pantalla,CREMA,(x-53,y-53,106,106),-math.pi/2,-math.pi/2+math.tau*max(0,carga["resta"])/7,3)
        return
    x,y = int(pos[0]),int(pos[1])
    for lado in (-1,1):
        oreja=[(x+lado*11,y-23),(x+lado*30,y-53),(x+lado*32,y-5)]
        pygame.draw.polygon(pantalla,(15,12,28),oreja)
        pygame.draw.polygon(pantalla,VIOLETA,[(x+lado*16,y-24),(x+lado*28,y-44),(x+lado*27,y-10)])
    for i in range(5):
        angulo = math.pi*.15+i*math.pi*.175
        a = (x+math.cos(angulo)*22,y+math.sin(angulo)*22)
        b = (x+math.cos(angulo)*43,y+math.sin(angulo)*43+math.sin(segundos*5+i)*7)
        pygame.draw.line(pantalla,LIMA,a,b,7)
        pygame.draw.circle(pantalla,LIMA,(int(b[0]),int(b[1])),4)
    pygame.draw.circle(pantalla,FONDO,(x,y),35)
    pygame.draw.circle(pantalla,(214,193,231),(x,y),31)
    for dx in (-12,12):
        pygame.draw.circle(pantalla,CREMA,(x+dx,y-17),11)
        pygame.draw.ellipse(pantalla,(118,43,108),(x+dx-5,y-23,10,17))
        pygame.draw.circle(pantalla,CREMA,(x+dx-2,y-20),3)
        pygame.draw.line(pantalla,FONDO,(x+dx-10,y-25),(x+dx+8,y-27),3)
    alto = 8 if cerrada else 26
    pygame.draw.ellipse(pantalla,(38,55,49),(x-22,y-6,44,alto))
    for dx in (-13,0,13):
        pygame.draw.polygon(pantalla,CREMA,[(x+dx-4,y-5),(x+dx+4,y-5),(x+dx,y+3)])
    if carga:
        bicho(pantalla,(x+28,y+25),False,segundos*5,.55)
        pygame.draw.arc(pantalla,CREMA,(x-41,y-41,82,82),-math.pi/2,-math.pi/2+math.tau*max(0,carga['resta'])/7,4)


def panel(pantalla, rect, color=(43, 32, 62), borde=(120, 85, 125)):
    """Compone el tablero que rodea la zona jugable."""
    pygame.draw.rect(pantalla,color,rect,border_radius=20)
    pygame.draw.rect(pantalla,borde,rect,2,border_radius=20)


def crear_escenario():
    """Jardín anime original: tinta violeta, luna, ramas y flores rosas."""
    ilustracion = Path(__file__).parent / "assets" / "jardin-anime-v1.png"
    if ilustracion.exists():
        fondo = pygame.transform.smoothscale(pygame.image.load(str(ilustracion)).convert(),(ANCHO,ALTO))
        velo = pygame.Surface((ANCHO,ALTO),pygame.SRCALPHA)
        velo.fill((20,12,36,65))
        fondo.blit(velo,(0,0))
        return fondo
    fondo = pygame.Surface((ANCHO,ALTO))
    for y in range(ALTO):
        t=y/ALTO
        pygame.draw.line(fondo,(int(25+15*t),int(19+10*t),int(40+22*t)),(0,y),(ANCHO,y))
    pygame.draw.circle(fondo,(92,65,104),(815,80),66)
    pygame.draw.circle(fondo,(233,210,220),(815,80),48)
    pygame.draw.circle(fondo,(209,180,205),(831,67),12)
    rng=random.Random(27)
    for lado in (-1,1):
        borde=0 if lado==1 else ANCHO
        for j in range(9):
            y=90+j*75
            x=borde+lado*rng.randint(4,37)
            pygame.draw.line(fondo,(62,74,76),(x,y+100),(x+lado*30,y-35),4)
            for k in range(4):
                yy=y+k*23
                xx=x+lado*(20-k*5)
                pygame.draw.ellipse(fondo,(65+j%3*12,83,91),(xx-18,yy-7,36,13))
            if j%2==0:
                cx=x+lado*36
                for a in range(5):
                    ang=a*math.tau/5
                    pygame.draw.circle(fondo,(165,85,137),(int(cx+math.cos(ang)*9),int(y+math.sin(ang)*9)),7)
                pygame.draw.circle(fondo,(247,205,158),(cx,y),4)
    for _ in range(70):
        x,y=rng.randrange(ANCHO),rng.randrange(ALTO)
        pygame.draw.circle(fondo,(121,87,129),(x,y),1)
    return fondo


def guia_camara(pantalla, frame, control, fuentes, cerrada, pequena=False):
    """Vista espejo pequeña: el marco marca el recorrido cómodo de dedos."""
    rect=pygame.Rect(12,105,156,117) if pequena else pygame.Rect(666,112,244,183)
    panel(pantalla,rect.inflate(10,10))
    mini=redimensionar(frame,rect.size)
    pantalla.blit(pygame.image.frombuffer(mini.tobytes(),rect.size,'BGR'),rect)
    puntos=getattr(control,'puntos',[])
    if len(puntos)==21:
        posiciones=[(round(rect.x+x*rect.w),round(rect.y+y*rect.h)) for x,y,z in puntos]
        for a,b in control.conexiones:
            pygame.draw.line(pantalla,(198,232,166),posiciones[a],posiciones[b],2)
        for punto in posiciones:
            pygame.draw.circle(pantalla,(29,53,49),punto,4)
            pygame.draw.circle(pantalla,(255,218,136),punto,2)
    zona=rect.inflate(-8,-8)
    pygame.draw.rect(pantalla,LIMA,zona,2,border_radius=6)
    if control.punto_camara is not None:
        px,py=control.punto_camara
        pygame.draw.circle(pantalla,CREMA,(int(rect.x+px*rect.w),int(rect.y+py*rect.h)),6,2)
    texto(pantalla,fuentes,'PINZA CERRADA' if cerrada else 'PINZA ABIERTA',(rect.x+8,rect.bottom-23),18,LIMA)
    texto(pantalla,fuentes,'ZONA SEGURA' if pequena else 'Dedos dentro del marco rosa',(rect.x,rect.bottom+12),18)


def main():
    """Ejecuta el menú y las cuatro aventuras con la misma cámara y ventana."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera', type=int, default=0)
    args = parser.parse_args()
    pygame.mixer.pre_init(44100,-16,2,512)
    pygame.init()
    limpiar_cache()  # Las fuentes SDL no sobreviven a pygame.quit().
    sonido = Sonido()
    ancho_vista=1280
    margen=(ancho_vista-ANCHO)//2
    ventana = pygame.display.set_mode((ancho_vista,ALTO), pygame.RESIZABLE)
    lienzo=pygame.Surface((ancho_vista,ALTO))
    contenido=pygame.Surface((ANCHO,ALTO))
    pantalla=contenido
    identidad=Identidad()
    logo_menu=None
    if identidad.logo is not None:
        lw,lh=identidad.logo.get_size()
        factor=min(460/lw,120/lh)
        logo_menu=pygame.transform.smoothscale(identidad.logo,(round(lw*factor),round(lh*factor)))
    frame_reflejo=None
    tam_reflejo=None
    reflejo=None
    ultima_medicion=0
    completa = False
    escritorio = pygame.display.get_desktop_sizes()[0]
    def coordenadas_raton():
        """Convierte la posición del mouse al espacio del lienzo, excluyendo las bandas."""
        w,h = ventana.get_size()
        escala = min(w/ancho_vista,h/ALTO)
        mx,my = pygame.mouse.get_pos()
        x=(mx-(w-ancho_vista*escala)/2)/escala
        return (x if estado=="menu" else x-margen,(my-(h-ALTO*escala)/2)/escala)
    pygame.display.set_caption(NOMBRE+' · Esc: menú')
    fuentes = {tam:(lectura(tam) if tam<=28 else fuente(tam)) for tam in (18,22,24,28,34,42,56,76)}
    escenario = crear_escenario()
    ambiente = Ambiente(escenario)
    atlas=pygame.image.load(str(Path(__file__).parent/'assets'/'mundos-bosque-v3.png')).convert()
    aw,ah=atlas.get_size()
    mundos=[]
    for i in range(4):
        x0,x1=round(i%2*aw/2),round((i%2+1)*aw/2)
        y0,y1=round(i//2*ah/2),round((i//2+1)*ah/2)
        mundos.append(Ambiente(atlas.subsurface((x0,y0,x1-x0,y1-y0)).copy()))
    cocina_ruta = Path(__file__).parent / "assets" / "cocina-anime-v1.png"
    cocina = Ambiente(pygame.transform.smoothscale(pygame.image.load(str(cocina_ruta)).convert(),(ANCHO,ALTO))) if cocina_ruta.exists() else Ambiente(escenario)
    reloj = pygame.time.Clock()
    control = None
    ancho_control_anterior=ANCHO
    entrada = None
    frame = None
    estado = 'menu'
    partida = None
    elegido = 1
    nivel = 0
    practica_lista = False
    particulas = Particulas()
    efectos = Efectos()
    pausado = False
    cerrada = False
    pos = None
    sin_mano = True
    error = ''
    mostrar_camara = False
    celebracion = 0.0
    cuenta_inicio=0.0
    estrellas = [(random.randrange(ANCHO),random.randrange(120,635),random.randint(1,2)) for _ in range(55)]
    bosque_ruta=Path(__file__).parent/"assets"/"inicio-bosque-v2.png"
    bosque=Ambiente(pygame.transform.smoothscale(pygame.image.load(str(bosque_ruta)).convert(),(ANCHO,ALTO))) if bosque_ruta.exists() else ambiente
    coleccion = Coleccion()
    diario = Diario()
    companero = Companero()
    regreso = Regreso()
    jugar = pygame.Rect(305,522,350,62)
    repetir = REPETIR
    try:
        entrada = abrir_camara(args.camera)
        if entrada is None:
            error = 'No se pudo abrir la cámara. Cerrá otras apps y reiniciá el juego.'
        andando = True
        while andando:
            dt = min(reloj.tick(FPS)/1000, .08)
            ahora = pygame.time.get_ticks()/1000
            if ahora-ultima_medicion>.5:
                pygame.display.set_caption(f'{NOMBRE} · {reloj.get_fps():.0f} FPS · Esc: menú')
                ultima_medicion=ahora
            click = False
            mordida = False
            for evento in pygame.event.get():
                if evento.type in (pygame.QUIT,pygame.WINDOWCLOSE):
                    andando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        if estado == 'menu':
                            andando = False
                        else:
                            estado = 'menu'
                    elif evento.key in (pygame.K_LEFT,pygame.K_RIGHT) and estado=='menu':
                        coleccion.mover(-1 if evento.key==pygame.K_LEFT else 1)
                    elif evento.key == pygame.K_r and estado=='juego' and elegido==4:
                        partida.reiniciar_trazo()
                    elif evento.key == pygame.K_d and estado in ('menu','resultado','diario'):
                        estado='menu' if estado=='diario' else 'diario'
                    elif evento.key == pygame.K_m:
                        sonido.alternar()
                    elif evento.key == pygame.K_c:
                        mostrar_camara = not mostrar_camara
                    elif evento.key == pygame.K_F11:
                        completa = not completa
                        ventana = pygame.display.set_mode(escritorio,pygame.NOFRAME) if completa else pygame.display.set_mode((ancho_vista,ALTO),pygame.RESIZABLE)
                    elif evento.key == pygame.K_p and estado == 'juego':
                        pausado = not pausado
                    elif estado == 'instrucciones' and evento.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        opcion = evento.key - pygame.K_1
                        if diario.disponible(elegido, opcion):
                            nivel = opcion
                    elif evento.key in (pygame.K_RETURN,pygame.K_1,pygame.K_2,pygame.K_3,pygame.K_4):
                        if estado == 'menu':
                            elegido = coleccion.indice+1 if evento.key==pygame.K_RETURN else {pygame.K_2:2,pygame.K_3:3,pygame.K_4:4}.get(evento.key,1)
                            nivel = min(diario.niveles(elegido), 2)
                            estado = 'instrucciones'
                        elif estado in ('instrucciones','resultado') and evento.key==pygame.K_RETURN:
                            if estado == 'instrucciones' and elegido == 1 and nivel == 0 and not practica_lista:
                                continue
                            if estado == 'resultado':
                                nivel = diario.siguiente(elegido, nivel, partida)
                            partida = {1:Partida,2:Faroles,3:Banquete,4:Sellos}[elegido](nivel)
                            efectos = Efectos()
                            particulas = Particulas()
                            estado, pausado = 'juego',False
                elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    click = True
            if not andando:
                break

            if entrada is not None:
                ancho_control=ancho_vista if estado=='menu' else ANCHO
                referencia = 'indice'
                if estado == 'menu' or (estado == 'juego' and elegido == 3):
                    referencia = 'palma'
                elif estado == 'juego' and elegido == 4:
                    referencia = 'pinza'
                entrada.configurar(ancho_control,ALTO,referencia)
                muestra=entrada.leer()
                if muestra is not None:
                    frame,pos,cerrada,mordida,control=muestra
                    error=''
                else:
                    pos, cerrada = None, False
                    error = 'Esperando imagen de la cámara…'
            if estado == 'menu' and control is not None:
                pos = pos if control.puntos else None
            sin_mano = pos is None
            sonido.juego = elegido
            if estado=='juego' and getattr(companero,'partida',None) is not partida:
                companero=Companero()
                companero.partida=partida
                cuenta_inicio=3.0
                if elegido==3: partida.cuenta=0
            if estado=='juego' and not pausado and not sin_mano:
                particulas.actualizar(dt)
            preparando=estado=='juego' and cuenta_inicio>0
            if preparando and not pausado and not sin_mano:
                cuenta_inicio=max(0,cuenta_inicio-dt)
            paso_dt=0 if preparando else dt
            activar = click or mordida
            puntero = coordenadas_raton() if click else pos
            if mordida and control is not None:
                puntero=getattr(control,'pos_evento',None) or pos

            fondo_activo = bosque if estado in ('menu','diario','resultado') else mundos[elegido-1]
            fondo_activo.actualizar(0 if estado=="juego" and (pausado or sin_mano) else dt)
            render_menu=estado=='menu'
            fondo_activo.dibujar(lienzo)
            if estado!='juego':
                pygame.draw.rect(lienzo,MUSGO,(0,665,ancho_vista,55))
            if estado=='juego':
                pygame.draw.rect(lienzo,MUSGO,(0,0,ancho_vista,98))
                borde_footer=645 if elegido==1 else 620
                pygame.draw.rect(lienzo,MUSGO,(0,borde_footer,ancho_vista,ALTO-borde_footer))
            if render_menu:
                pantalla=lienzo
            else:
                pantalla=contenido
                pantalla.blit(lienzo,(-margen,0))
            if estado=='juego' and frame is not None:
                if frame is not frame_reflejo or tam_reflejo!=(ANCHO,ALTO):
                    cam=redimensionar(frame,(ANCHO,ALTO))
                    reflejo=pygame.image.frombuffer(cam.tobytes(),(ANCHO,ALTO),'BGR').copy()
                    reflejo.set_alpha(48)
                    frame_reflejo=frame
                    tam_reflejo=(ANCHO,ALTO)
                pantalla.blit(reflejo,(78,130),(78,130,804,478))
            if estado == 'instrucciones':
                panel_papel(pantalla,(42,40,876,604))
            if estado == 'menu':
                velo=pygame.Surface((ancho_vista,ALTO),pygame.SRCALPHA)
                velo.fill((241,231,201,24))
                pantalla.blit(velo,(0,0))

                pie=pygame.Surface((ancho_vista,55),pygame.SRCALPHA)
                pie.fill((34,57,39,190))
                pantalla.blit(pie,(0,665))
                if logo_menu is not None:
                    pantalla.blit(logo_menu,logo_menu.get_rect(center=(640,73)))
                palma=pos
                abierta=control is not None and bool(control.puntos)
                coleccion.actualizar(dt,[palma],gesto=abierta,cerrada=cerrada)
                coleccion.dibujar(pantalla)
                if frame is not None:
                    if frame is not frame_reflejo or tam_reflejo!=(ancho_vista,ALTO):
                        espejo=redimensionar(frame,(ancho_vista,ALTO))
                        reflejo=pygame.image.frombuffer(espejo.tobytes(),(ancho_vista,ALTO),'BGR').copy()
                        reflejo.set_alpha(44)
                        frame_reflejo=frame
                        tam_reflejo=(ancho_vista,ALTO)
                    pantalla.blit(reflejo,(0,142),(0,142,ancho_vista,490))
                diario.insignias(pantalla,coleccion.rects)
                # Los primeros recuerdos aparecen junto a la carta como habitantes de la casita.
                for i, centro in enumerate(((188, 552), (1084, 552), (290, 573), (987, 575))):
                    if diario.niveles(i + 1) > 0:
                        recuerdo(pantalla, centro, i, 68, True, ahora)
                diario.boton_menu(pantalla,puntero)
                if click or (mordida and puntero is not None and DIARIO_MENU.collidepoint(puntero)) or (coleccion.listo):
                    if puntero and DIARIO_MENU.collidepoint(puntero):
                        estado='diario'
                    else:
                        seleccion=coleccion.seleccionar(puntero)
                        if seleccion is not None:
                            elegido=seleccion
                            nivel = min(diario.niveles(elegido), 2)
                            estado='instrucciones'
                if not palma and diario.sellos == 0:
                    fase = min(1, (ahora % 3) / 1.5)
                    mano_lateral(pantalla, (250 - 95 * fase, 634), 0, 55)
                    pygame.draw.line(pantalla, PAPEL, (259, 626), (154, 626), 2)
                    pygame.draw.polygon(pantalla, PAPEL, [(146,626),(156,621),(156,631)])
                escribir(pantalla,'Mostrá la palma · Deslizá de derecha a izquierda · Dejala quieta sobre una carta para abrir',(640,691),21,PAPEL)

            elif estado == 'diario':
                regresar=diario.album(pantalla,coleccion,pos,dt)
                if activar and puntero and regresar.collidepoint(puntero): estado='menu'

            elif estado == 'instrucciones':
                escribir(pantalla,'CÓMO JUGAR',(480,74),19,negrita=True)
                escribir(pantalla,{1:'Bichos a la boca',2:'Faroles del jardín',3:'Banquete del familiar',4:'Sellos de luna'}[elegido],(480,126),48,titulo=True,ancho=770)
                separador(pantalla,480,180,300)
                pasos = {
                    1: [('Acercá la boca', 'Mové la mano con los dedos abiertos.'),
                        ('Hacé pinza', 'Juntá pulgar e índice sobre un bicho amarillo.'),
                        ('Soltá en la bolsa', 'Llevá el bicho y abrí los dedos.')],
                    2: [('Mirá los faroles', 'Esperá a que termine la secuencia.'),
                        ('Repetí en orden', 'Juntá pulgar e índice sobre cada farol.'),
                        ('Abrí entre toques', 'Separá los dedos antes del siguiente.')],
                    3: [('Mové la palma', 'Llevá la canasta a izquierda o derecha.'),
                        ('Recogé dulces', 'Alineá la canasta debajo del objeto.'),
                        ('Esquivá peligros', 'Alejate de pociones y bombas.')],
                    4: [('Apuntá a la joya', 'Llevá la punta de la pluma al inicio.'),
                        ('Cerrá la pinza', 'Juntá pulgar e índice para dibujar.'),
                        ('Seguí la guía', 'Mantené la pinza y seguí el punto.')],
                }[elegido]
                for i, (titulo_paso, detalle) in enumerate(pasos):
                    xx = 72 + i * 278
                    panel_papel(pantalla, (xx, 211, 260, 230), (236, 229, 203))
                    escribir(pantalla, titulo_paso, (xx + 130, 237), 26, negrita=True, ancho=232)
                    demo = pygame.Surface((240, 110), pygame.SRCALPHA)
                    animar_tutorial(demo, elegido, i, ahora)
                    pantalla.blit(demo, (xx + 10, 254))
                    palabras = detalle.split()
                    mitad = (len(palabras) + 1) // 2
                    for fila, frase in enumerate((' '.join(palabras[:mitad]), ' '.join(palabras[mitad:]))):
                        escribir(pantalla, frase, (xx + 130, 385 + 26 * fila), 20, ancho=232)
                for i in range(3):
                    selector = pygame.Rect(210 + i * 184, 453, 172, 36)
                    disponible = diario.disponible(elegido, i)
                    sobre = disponible and puntero is not None and selector.collidepoint(puntero)
                    if activar and sobre:
                        nivel = i
                    elegido_nivel = nivel == i
                    color = MUSGO if elegido_nivel else (228, 218, 188)
                    pygame.draw.rect(pantalla, color, selector, border_radius=8)
                    if sobre:
                        pygame.draw.rect(pantalla, MUSGO, selector, 2, border_radius=8)
                    etiqueta = f'Nivel {i + 1}' if disponible else f'Nivel {i + 1} · Cerrado'
                    escribir(pantalla, etiqueta, selector.center, 19,
                             PAPEL if elegido_nivel else MUSGO, negrita=elegido_nivel)
                segundos, meta = NIVELES_AVENTURAS[elegido - 1][nivel]
                unidad = ('bichitos', 'constelaciones', 'puntos', 'sellos')[elegido - 1]
                escribir(pantalla, f'{meta} {unidad} en {int(segundos)} s', (480, 505), 22, negrita=True)
                requiere_practica = elegido == 1 and nivel == 0 and not practica_lista
                if requiere_practica:
                    blanco = pygame.Rect(420, 266, 120, 100)
                    pygame.draw.rect(pantalla, MUSGO, blanco, 2, border_radius=14)
                    if mordida and puntero is not None and blanco.collidepoint(puntero):
                        practica_lista = True
                        requiere_practica = False
                if requiere_practica:
                    panel_papel(pantalla, jugar)
                    escribir(pantalla, 'Practicá una pinza arriba', jugar.center, 26, negrita=True)
                else:
                    boton(pantalla,jugar,'Comenzar la aventura',puntero is not None and jugar.collidepoint(puntero))
                    if activar and puntero is not None and jugar.collidepoint(puntero):
                        partida={1:Partida,2:Faroles,3:Banquete,4:Sellos}[elegido](nivel)
                        efectos = Efectos()
                        particulas = Particulas()
                        estado,pausado='juego',False
                avisos_bichos = ('Hacé pinza en el recuadro · El reloj todavía está quieto',
                                 'Acercate despacio para que el bicho no escape',
                                 'Los bichos con luna van a la izquierda y los de sol a la derecha')
                aviso = 'Completá el nivel para abrir el siguiente · Enter para empezar'
                if elegido == 1 and (requiere_practica or nivel):
                    aviso = avisos_bichos[nivel]
                elif elegido == 2 and nivel:
                    aviso = ('Seguí el contorno del jardín' if nivel == 1
                             else 'Los faroles se ocultan: repetí el orden sobre sus huellas')
                elif elegido == 3 and nivel:
                    aviso = ('Juntá el dulce que pide el familiar para sumar un bonus' if nivel == 1
                             else 'Recogé los ingredientes en el orden del pedido')
                escribir(pantalla, aviso, (480,619),20,ancho=800)

            elif estado == 'juego' and elegido in (2,3,4):
                if not pausado and not preparando:
                    partida.actualizar(paso_dt,pos,cerrada,False if preparando else mordida)
                    sonido.recibir(partida.eventos)
                    particulas.recibir(partida.eventos,elegido)
                    companero.actualizar(0 if sin_mano else dt,partida.eventos)
                    partida.eventos.clear()
                partida.dibujar(pantalla,fuentes,ahora)
                if pausado or sin_mano:
                    velo=pygame.Surface((ANCHO,ALTO),pygame.SRCALPHA)
                    velo.fill((9,18,25,185))
                    pantalla.blit(velo,(0,0))
                    texto(pantalla,fuentes,'PAUSA' if pausado else 'MOSTRÁ TU MANO',(480,310),56,CREMA,True)
                    texto(pantalla,fuentes,'P para continuar' if pausado else 'El juego y el tiempo están detenidos.',(480,366),28,LIMA,True)
                if partida.fin:
                    diario.registrar(elegido,partida,nivel)
                    estado='resultado'

            elif estado == 'juego':
                puntos_antes = partida.puntos
                if not pausado and not preparando:
                    partida.actualizar(paso_dt,pos,cerrada,False if preparando else mordida)
                    efectos.recibir(partida.eventos)
                    sonido.recibir(partida.eventos)
                    particulas.recibir(partida.eventos,elegido)
                    companero.actualizar(0 if sin_mano else dt,partida.eventos)
                    partida.eventos.clear()
                    if pos is not None or partida.fin:
                        efectos.actualizar(dt)
                if partida.puntos > puntos_antes:
                    celebracion = 1.2
                celebracion = max(0,celebracion-dt)
                cabecera(pantalla,1,'Bichos a la boca','CAPTURA · TU BOLSITA DEL BOSQUE','BICHITOS A SALVO',partida.puntos,partida.meta,partida.tiempo)
                pygame.draw.rect(pantalla,(117,142,86),(78,130,804,478),1,border_radius=30)
                efectos.bolsa(pantalla,partida.carga is not None,ahora,bicho)
                panel_papel(pantalla,(NIDO[0]-105,NIDO[1]-108,210,33))
                escribir(pantalla,'Soltá acá' if partida.carga and partida.refugio() == NIDO else f'{partida.puntos} / {partida.meta} bichitos',(NIDO[0],NIDO[1]-91),18,negrita=True)
                panel_papel(pantalla,(NIDO[0]-109,NIDO[1]+130,218,30))
                escribir(pantalla,'Bolsa Sol' if partida.nivel == 2 else 'Bolsita del bosque',(NIDO[0],NIDO[1]+145),18,negrita=True)
                if partida.nivel == 2:
                    pygame.draw.ellipse(pantalla, (217, 201, 245),
                                        (REFUGIO_LUNA[0]-85, REFUGIO_LUNA[1]-56, 170, 112), 4)
                    panel_papel(pantalla, (REFUGIO_LUNA[0]-74, REFUGIO_LUNA[1]-78, 148, 33))
                    escribir(pantalla, 'Luna · Soltá acá' if partida.carga and partida.carga.get('luna') else 'Bolsa Luna',
                             (REFUGIO_LUNA[0], REFUGIO_LUNA[1]-61), 18, negrita=True)
                for b in partida.bichos:
                    bicho(pantalla,(b['x'],b['y']),b['malo'],b['fase'])
                    if b.get('asustado'):
                        escribir(pantalla,'!', (b['x'],b['y']-33),24,CREMA,negrita=True)
                    elif partida.nivel == 2 and not b['malo']:
                        pygame.draw.circle(pantalla, (111,87,141) if b.get('luna') else (166,107,39),
                                           (round(b['x']),round(b['y']-30)),11)
                        escribir(pantalla,'L' if b.get('luna') else 'S',(b['x'],b['y']-30),14,CREMA,negrita=True)
                mensaje = partida.mensaje if partida.aviso>0 else ('Mantené la pinza y soltá en la bolsita' if partida.carga else 'Acercate a un bichito y cerrá la pinza')
                panel_pie(pantalla,mensaje,compacto=True)
                if pausado or sin_mano:
                    velo=pygame.Surface((ANCHO,ALTO),pygame.SRCALPHA)
                    velo.fill((9,18,25,165))
                    pantalla.blit(velo,(0,0))
                    texto(pantalla,fuentes,'PAUSA' if pausado else '¿Dónde está mi monstruo?',(480,310),56,CREMA,True)
                    texto(pantalla,fuentes,'P para continuar' if pausado else 'Mostrá la mano completa. El tiempo está detenido.',(480,366),28,LIMA,True)
                if celebracion > 0:
                    texto(pantalla,fuentes,'+1 ¡ÑAM!',(NIDO[0],NIDO[1]-125-int((1.2-celebracion)*22)),34,LIMA,True)
                if partida.fin and not efectos.caidas and efectos.golpe <= 0:
                    diario.registrar(elegido,partida,nivel)
                    estado='resultado'

            elif estado == 'resultado':
                diario.resultado(pantalla,elegido,partida,ahora,nivel)
                if activar and puntero is not None and repetir.collidepoint(puntero):
                    nivel = diario.siguiente(elegido, nivel, partida)
                    partida={1:Partida,2:Faroles,3:Banquete,4:Sellos}[elegido](nivel)
                    efectos = Efectos()
                    particulas = Particulas()
                    estado,pausado='juego',False
                elif activar and puntero and VOLVER.collidepoint(puntero):
                    estado='menu'

            if estado=='juego':
                particulas.dibujar(pantalla,fuentes)
            if estado=='juego' and preparando and not sin_mano and not pausado:
                panel_papel(pantalla,(310,235,340,190))
                escribir(pantalla,str(max(1,math.ceil(cuenta_inicio))),(480,300),76,negrita=True)
                escribir(pantalla,'¡Prepará tu mano!',(480,386),26,titulo=True)
            if estado!='menu':
                regreso.dibujar(pantalla)
            if mostrar_camara and frame is not None:
                guia_camara(pantalla,frame,control,fuentes,cerrada,estado=="juego" and elegido in (2,3,4))
            if pos is not None and estado=='menu':
                cursor_cartas(pantalla,pos,cerrada)
            elif pos is not None and estado!='juego':
                cursor_faroles(pantalla,pos,cerrada,ahora)
            elif pos is not None and estado=='juego' and elegido==3:
                pass  # La canasta es el cursor de este juego.
            elif pos is not None and estado=='juego' and elegido==4:
                cursor_sellos(pantalla,partida.punta or pos,cerrada,ahora)
            elif pos is not None and estado=='juego' and elegido==2:
                cursor_faroles(pantalla,pos,cerrada,ahora)
            elif pos is not None:
                dibujo_pos = (pos[0]+math.sin(ahora*65)*5,pos[1]) if estado=='juego' and efectos.golpe else pos
                objetivo=None
                if estado=='juego' and partida.bichos and not partida.carga:
                    cercano=min(partida.bichos,key=lambda b:math.dist(pos,(b['x'],b['y'])))
                    objetivo=(cercano['x'],cercano['y'])
                dibujo_pos,angulo=companero.postura(dibujo_pos,objetivo)
                monstruo(pantalla,dibujo_pos,cerrada,ahora,partida.carga if estado=='juego' else None,angulo)
                companero.dibujar(pantalla,dibujo_pos)
                if estado=='juego':
                    efectos.dibujar_picadura(pantalla,dibujo_pos,ahora,fuentes)
            if estado not in ('juego','menu'):
                texto(pantalla,fuentes,'MANO DETECTADA' if pos else 'MOSTRÁ TU MANO',(80 if render_menu else 48,ALTO-34),18,LIMA if pos else CORAL)
            if estado not in ('juego','menu'):
                texto(pantalla,fuentes,'SIN AUDIO' if not sonido.activo else ('M · SILENCIADO' if sonido.silenciado else 'M · SONIDO'),(540 if render_menu else 340,ALTO-34),18,CORAL if sonido.silenciado or not sonido.activo else CREMA)
            sonido.actualizar(estado,estado=='juego' and (pausado or sin_mano),partida is not None and partida.puntos>=partida.meta)
            if error:
                pygame.draw.rect(pantalla,(100,40,45),(0,ALTO-58,ANCHO,26))
                texto(pantalla,fuentes,error,(20,ALTO-54),22)
            if estado!='menu':
                if regreso.actualizar(dt,estado,puntero,cerrada,click or mordida):
                    estado='menu'
                    pausado=False
            else:
                regreso.actualizar(dt,estado,None,False)
            w,h = ventana.get_size()
            escala = min(w/ancho_vista,h/ALTO)
            medida = (round(ancho_vista*escala),round(ALTO*escala))
            if not render_menu:
                lienzo.blit(contenido,(margen,0))
                if estado=='juego':
                    guia_gesto(lienzo,pos,cerrada,elegido,getattr(partida,'carga',None),control,False)
                    if elegido!=1:
                        mascota,angulo=companero.postura((1200,350))
                        dibujar_familiar(lienzo,mascota,True,companero.t,angulo)
                        companero.dibujar(lienzo,mascota)
                        panel_papel(lienzo,(1130,413,140,34))
                        escribir(lienzo,'Tu compañero',(1200,430),16,negrita=True)
            ventana.fill(FONDO)
            vista=lienzo if medida==lienzo.get_size() else pygame.transform.smoothscale(lienzo,medida)
            ventana.blit(vista,((w-medida[0])//2,(h-medida[1])//2))
            pygame.display.flip()
    finally:
        sonido.cerrar()
        pygame.quit()
        if entrada is not None:
            entrada.cerrar()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'No se pudo continuar: {error}',file=sys.stderr)
        raise
