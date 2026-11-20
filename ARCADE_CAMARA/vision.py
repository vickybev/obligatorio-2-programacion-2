"""Captura, espejado y detección de la mano para el juego."""
import math
import threading
import time
from types import SimpleNamespace

import cv2
import mediapipe as mp

from ajustes import (
    ANCLA_PINZA_ENTRADA, ANCLA_PINZA_SALIDA, CAMARA_ALTO, CAMARA_ANCHO,
    CAMARA_FPS, CONFIANZA_MANO, FACTOR_DEDO_EXTENDIDO, MARGEN_CURSOR,
    MARGEN_MANO_NORMALIZADO, PINZA_APERTURA, PINZA_CIERRE, RETENCION_DETECCION,
)


def abrir_camara(preferida):
    """Inicia la captura con el primer dispositivo disponible."""
    indices = dict.fromkeys((preferida, 0, 1, 2))
    for indice in indices:
        camara = cv2.VideoCapture(indice, cv2.CAP_DSHOW)
        if not camara.isOpened():
            camara.release()
            continue
        try:
            camara.set(cv2.CAP_PROP_FRAME_WIDTH, CAMARA_ANCHO)
            camara.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMARA_ALTO)
            camara.set(cv2.CAP_PROP_FPS, CAMARA_FPS)
            camara.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            return EntradaCamara(camara, ControlMano())
        except Exception:
            camara.release()
            raise
    return None


def redimensionar(frame, medidas):
    """Adapta la imagen de cámara a una vista del juego."""
    return cv2.resize(frame, medidas)


class ControlMano:
    """Sigue una mano y detecta el gesto de pinza."""
    def __init__(self):
        """Crea el detector y prepara el estado del seguimiento."""
        self.detector = mp.solutions.hands.Hands(
            model_complexity=0,
            max_num_hands=1, min_detection_confidence=CONFIANZA_MANO,
            min_tracking_confidence=CONFIANZA_MANO,
        )
        self.ultima_deteccion = 0.0
        self.cerrada = False
        self.posicion = None
        self.punto_camara = None
        self.cerca_borde = False
        self.puntos = []
        self.posicion_palma = None
        self.mano_abierta = False
        self.conexiones = tuple(mp.solutions.hands.HAND_CONNECTIONS)
        self.referencia=None
        self.ancla_pinza=None
        self.ancla_palma=None

    def leer(self, frame, ancho, alto, referencia='pinza'):
        """Devuelve posición, pinza cerrada y transición de cierre."""
        resultado = self.detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not resultado.multi_hand_landmarks:
            self.puntos=[]
            self.mano_abierta=False
            if self.posicion is not None and time.monotonic()-self.ultima_deteccion<RETENCION_DETECCION:
                return self.posicion,self.cerrada,False
            self.cerca_borde = False
            self.punto_camara = None
            self.posicion = None
            self.posicion_palma = None
            self.cerrada = False
            self.ancla_pinza=None
            self.ancla_palma=None
            return None, False, False
        ahora=time.monotonic()
        dt=max(.008,min(.08,ahora-self.ultima_deteccion))
        self.ultima_deteccion=ahora
        puntos = resultado.multi_hand_landmarks[0].landmark
        self.puntos=[(p.x,p.y,p.z) for p in puntos]
        # Advertir por toda la mano, no solamente por el cursor de la pinza.
        self.cerca_borde = any(min(p.x,p.y,1-p.x,1-p.y)< MARGEN_MANO_NORMALIZADO for p in puntos)
        self.punto_camara = ((puntos[4].x+puntos[8].x)/2, (puntos[4].y+puntos[8].y)/2)
        # Las distancias se calculan en píxeles para respetar la proporción.
        h, w = frame.shape[:2]
        def distancia(a, b):
            """Mide la distancia entre dos puntos en píxeles del cuadro."""
            return math.hypot((a.x-b.x)*w, (a.y-b.y)*h)
        palma = max(distancia(puntos[0], puntos[9]), 1)
        extendidos=sum(distancia(puntos[0],puntos[punta])>distancia(puntos[0],puntos[articulacion])* FACTOR_DEDO_EXTENDIDO
                       for punta,articulacion in ((8,6),(12,10),(16,14),(20,18)))
        proporcion = distancia(puntos[4], puntos[8]) / palma
        anterior = self.cerrada
        # Dos umbrales evitan vibración cerca del límite de la pinza.
        if proporcion < PINZA_CIERRE:
            self.cerrada = True
        elif proporcion > PINZA_APERTURA:
            self.cerrada = False
        self.mano_abierta=extendidos>=3 and not self.cerrada
        centro=tuple(sum(getattr(puntos[i],eje) for i in (0,5,9,13,17))/5 for eje in ('x','y'))
        destino=(max(MARGEN_CURSOR,min(ancho-MARGEN_CURSOR,centro[0]*ancho)),max(MARGEN_CURSOR,min(alto-MARGEN_CURSOR,centro[1]*alto)))
        alpha_palma=1-math.exp(-dt/.025)
        self.posicion_palma=destino if self.posicion_palma is None else tuple(a+(b-a)*alpha_palma for a,b in zip(self.posicion_palma,destino))
        # El encuadre completo comparte coordenadas con la cámara visible.
        # No aplicar ganancia ni recorte central al cursor.
        punto=centro if referencia=='palma' else ((puntos[8].x,puntos[8].y) if referencia=='indice' else self.punto_camara)
        if referencia=='indice':
            # Al plegar el índice para pinzar, trasladar el cursor con la palma.
            # Así cerrar dedos no equivale a mover la mano.
            if proporcion< ANCLA_PINZA_ENTRADA and self.ancla_pinza is None:
                self.ancla_pinza=self.punto_anterior if self.referencia==referencia and hasattr(self,'punto_anterior') else punto
                self.ancla_palma=centro
            if self.ancla_pinza is not None:
                if proporcion> ANCLA_PINZA_SALIDA:
                    self.ancla_pinza=None
                    self.ancla_palma=None
                else:
                    punto=tuple(a+b-c for a,b,c in zip(self.ancla_pinza,centro,self.ancla_palma))
        else:
            self.ancla_pinza=None
            self.ancla_palma=None
        self.punto_anterior=punto
        self.punto_camara=punto
        objetivo = (
            max(MARGEN_CURSOR, min(ancho-MARGEN_CURSOR, punto[0]*ancho)),
            max(MARGEN_CURSOR, min(alto-MARGEN_CURSOR, punto[1]*alto)),
        )
        if self.posicion is None or self.referencia!=referencia:
            self.posicion = objetivo
        else:
            # Respuesta rápida al trasladar la mano; amortiguación al sostenerla.
            desplazamiento=math.dist(self.posicion,objetivo)
            tau=.018 if desplazamiento>25 else .04
            alpha=1-math.exp(-dt/tau)
            self.posicion = tuple(a + (b-a)*alpha for a, b in zip(self.posicion, objetivo))
        self.referencia=referencia
        return self.posicion, self.cerrada, self.cerrada and not anterior

    def cerrar(self):
        """Libera el detector de MediaPipe."""
        self.detector.close()


class EntradaCamara:
    """Publica la muestra de cámara más reciente desde un hilo."""
    def __init__(self,camara,detector):
        """Inicia el hilo que lee la cámara y mantiene la muestra reciente."""
        self.camara=camara
        self.detector=detector
        self.config=(1280,720,'palma')
        self.muestra=None
        self.pendiente=False
        self.pos_evento=None
        self.lock=threading.Lock()
        self.fin=threading.Event()
        self.hilo=threading.Thread(target=self._procesar,name='Camara-MediaPipe',daemon=True)
        self.hilo.start()

    def configurar(self,ancho,alto,referencia):
        """Cambia el área de control y descarta gestos de la pantalla anterior."""
        with self.lock:
            nueva=(ancho,alto,referencia)
            if nueva!=self.config:
                self.config=nueva
                self.pendiente=False
                self.pos_evento=None

    def _procesar(self):
        """Lee y espeja cuadros, ejecuta el detector y publica la muestra más reciente."""
        anterior=None
        try:
            while not self.fin.is_set():
                with self.lock:config=self.config
                t=time.perf_counter()
                ok,frame=self.camara.read()
                captura=(time.perf_counter()-t)*1000
                if not ok:
                    self.fin.wait(.03)
                    continue
                frame=cv2.flip(frame,1)
                if config!=anterior:
                    self.detector.posicion=None
                    self.detector.posicion_palma=None
                    self.detector.ancla_pinza=None
                    self.detector.ancla_palma=None
                    anterior=config
                t=time.perf_counter()
                pos,cerrada,mordida=self.detector.leer(frame,*config)
                control=SimpleNamespace(**{k:getattr(self.detector,k) for k in ('puntos','conexiones','punto_camara','cerca_borde','mano_abierta','posicion_palma')})
                control.captura_ms=captura
                control.deteccion_ms=(time.perf_counter()-t)*1000
                with self.lock:
                    if config==self.config:
                        self.muestra=(time.monotonic(),config,frame,pos,cerrada,control)
                        if mordida:self.pos_evento=pos
                        self.pendiente=self.pendiente or mordida
                        if pos is None:self.pendiente=False;self.pos_evento=None
        finally:
            self.detector.cerrar()

    def leer(self):
        """Devuelve una muestra vigente y consume la transición de pinza una sola vez."""
        with self.lock:
            if self.muestra is None or self.muestra[1]!=self.config:return None
            instante,_,frame,pos,cerrada,control=self.muestra
            if time.monotonic()-instante>RETENCION_DETECCION:return None
            mordida=self.pendiente
            control=SimpleNamespace(**vars(control),pos_evento=self.pos_evento if mordida else None)
            self.pendiente=False
            return frame,pos,cerrada,mordida,control

    def cerrar(self):
        """Solicita el fin del hilo y libera el dispositivo de captura."""
        self.fin.set()
        self.hilo.join(timeout=2)
        self.camara.release()
