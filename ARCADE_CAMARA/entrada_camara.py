"""Captura y MediaPipe fuera del dibujo; se consume solo la muestra más reciente."""
import threading
import time
from types import SimpleNamespace
import cv2


class EntradaCamara:
    def __init__(self,camara,detector):
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
        with self.lock:
            nueva=(ancho,alto,referencia)
            if nueva!=self.config:
                self.config=nueva
                self.pendiente=False
                self.pos_evento=None

    def _procesar(self):
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
        with self.lock:
            if self.muestra is None or self.muestra[1]!=self.config:return None
            instante,_,frame,pos,cerrada,control=self.muestra
            if time.monotonic()-instante>.55:return None
            mordida=self.pendiente
            control=SimpleNamespace(**vars(control),pos_evento=self.pos_evento if mordida else None)
            self.pendiente=False
            return frame,pos,cerrada,mordida,control

    def cerrar(self):
        self.fin.set()
        self.hilo.join(timeout=2)
