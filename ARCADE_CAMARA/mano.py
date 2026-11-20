"""Convierte la mano de MediaPipe en posición y gesto de pinza."""
import math
import time
import cv2
import mediapipe as mp


class ControlMano:
    def __init__(self):
        self.detector = mp.solutions.hands.Hands(
            model_complexity=0,
            max_num_hands=1, min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
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
            if self.posicion is not None and time.monotonic()-self.ultima_deteccion<.55:
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
        self.cerca_borde = any(min(p.x,p.y,1-p.x,1-p.y)<.08 for p in puntos)
        self.punto_camara = ((puntos[4].x+puntos[8].x)/2, (puntos[4].y+puntos[8].y)/2)
        # Las distancias se calculan en píxeles para respetar la proporción.
        h, w = frame.shape[:2]
        def distancia(a, b):
            return math.hypot((a.x-b.x)*w, (a.y-b.y)*h)
        palma = max(distancia(puntos[0], puntos[9]), 1)
        extendidos=sum(distancia(puntos[0],puntos[punta])>distancia(puntos[0],puntos[articulacion])*1.12
                       for punta,articulacion in ((8,6),(12,10),(16,14),(20,18)))
        proporcion = distancia(puntos[4], puntos[8]) / palma
        anterior = self.cerrada
        # Dos umbrales evitan vibración cerca del límite de la pinza.
        if proporcion < 0.38:
            self.cerrada = True
        elif proporcion > 0.58:
            self.cerrada = False
        self.mano_abierta=extendidos>=3 and not self.cerrada
        centro=tuple(sum(getattr(puntos[i],eje) for i in (0,5,9,13,17))/5 for eje in ('x','y'))
        destino=(max(20,min(ancho-20,centro[0]*ancho)),max(20,min(alto-20,centro[1]*alto)))
        alpha_palma=1-math.exp(-dt/.025)
        self.posicion_palma=destino if self.posicion_palma is None else tuple(a+(b-a)*alpha_palma for a,b in zip(self.posicion_palma,destino))
        # El encuadre completo comparte coordenadas con la cámara visible.
        # No aplicar ganancia ni recorte central al cursor.
        punto=centro if referencia=='palma' else ((puntos[8].x,puntos[8].y) if referencia=='indice' else self.punto_camara)
        if referencia=='indice':
            # Al plegar el índice para pinzar, trasladar el cursor con la palma.
            # Así cerrar dedos no equivale a mover la mano.
            if proporcion<.85 and self.ancla_pinza is None:
                self.ancla_pinza=self.punto_anterior if self.referencia==referencia and hasattr(self,'punto_anterior') else punto
                self.ancla_palma=centro
            if self.ancla_pinza is not None:
                if proporcion>.95:
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
            max(20, min(ancho-20, punto[0]*ancho)),
            max(20, min(alto-20, punto[1]*alto)),
        )
        if self.posicion is None or self.referencia!=referencia:
            self.posicion = objetivo
        else:
            # Respuesta rápida al trasladar la mano; amortiguación al sostenerla.
            distancia=math.dist(self.posicion,objetivo)
            tau=.018 if distancia>25 else .04
            alpha=1-math.exp(-dt/tau)
            self.posicion = tuple(a + (b-a)*alpha for a, b in zip(self.posicion, objetivo))
        self.referencia=referencia
        return self.posicion, self.cerrada, self.cerrada and not anterior

    def cerrar(self):
        self.detector.close()
