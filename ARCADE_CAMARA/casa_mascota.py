"""Rincón persistente del compañero de La casita."""
import json
import math

import pygame

from interfaz import boton, escribir, papel, PAPEL, MUSGO, TINTA
from personajes import dibujar_familiar
from armario import PRENDAS

CUIDADOS = ('Comida', 'Baño', 'Juego', 'Caricias')
BOTONES = tuple(pygame.Rect(92 + i * 195, 527, 186, 55) for i in range(4))
MASCOTA = pygame.Rect(385, 216, 190, 170)
ABRIR_ARMARIO = pygame.Rect(700, 75, 171, 50)


class CasaMascota:
    """Guarda interacciones del compañero sin penalizar el paso del tiempo."""
    def __init__(self, ruta_diario):
        """Recupera los cuidados asociados a este perfil."""
        self.ruta = ruta_diario.with_name('mascota.json')
        try:
            datos = json.loads(self.ruta.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            datos = {}
        self.cuidados = {
            accion: datos[accion] if isinstance(datos, dict) and type(datos.get(accion)) is int
            and datos[accion] >= 0 else 0 for accion in CUIDADOS
        }
        prenda = datos.get('prenda') if isinstance(datos, dict) else None
        self.prenda = tuple(prenda) if isinstance(prenda, list) and len(prenda) == 2 and all(
            type(i) is int for i in prenda) and 0 <= prenda[0] < 4 and 0 <= prenda[1] < 3 else None
        self.armario = False
        self.mensaje = 'Tu compañero está feliz de verte'
        self.accion = None
        self.hasta = 0

    def cuidar(self, accion, ahora):
        """Suma el cuidado, responde con una animación y guarda el estado."""
        self.cuidados[accion] += 1
        self.accion = accion
        self.hasta = ahora + 1.8
        self.mensaje = {
            'Comida': '¡Ñam! Se comió un bocadito',
            'Baño': '¡Listo! Quedó limpito',
            'Juego': '¡Otra vez! Le encantó jugar',
            'Caricias': 'Cerró los ojos de lo contento que está',
        }[accion]
        self.guardar()

    def guardar(self):
        """Guarda los cuidados y la única prenda que está puesta."""
        temporal = self.ruta.with_suffix('.tmp')
        try:
            self.ruta.parent.mkdir(parents=True, exist_ok=True)
            temporal.write_text(json.dumps({**self.cuidados, 'prenda': self.prenda}, ensure_ascii=False), encoding='utf-8')
            temporal.replace(self.ruta)
        except OSError:
            self.mensaje = 'El cuidado quedó en esta sesión. No se pudo guardar.'

    def equipar(self, prenda, diario):
        """Equipa una prenda ganada o vuelve al aspecto original."""
        if prenda is not None and prenda[1] >= diario.niveles(prenda[0] + 1):
            return
        self.prenda = prenda
        self.guardar()

    def dibujar_armario(self, pantalla, puntero, activar, ahora, diario):
        """Muestra prendas ganadas, bloqueadas y la que está puesta."""
        papel(pantalla, (53,40,854,600))
        escribir(pantalla,'Armario de tu compañero',(480,95),38,titulo=True)
        dibujar_familiar(pantalla,(188,268),True,ahora,prenda=self.prenda)
        nombre = PRENDAS[self.prenda[0]][self.prenda[1]] if self.prenda is not None else 'Aspecto original'
        escribir(pantalla, nombre, (188,360),19,negrita=True,ancho=190)
        volver = pygame.Rect(82,512,192,46)
        quitar = pygame.Rect(82,455,192,46)
        boton(pantalla,volver,'Volver a la casa')
        boton(pantalla,quitar,'Aspecto original')
        if activar and puntero is not None:
            if volver.collidepoint(puntero):
                self.armario = False
                return
            if quitar.collidepoint(puntero):
                self.equipar(None, diario)
        for grupo, prendas in enumerate(PRENDAS):
            for nivel, nombre_prenda in enumerate(prendas):
                rect = pygame.Rect(294+nivel*190,162+grupo*88,182,73)
                ganada = nivel < diario.niveles(grupo + 1)
                puesta = self.prenda == (grupo, nivel)
                if ganada and activar and puntero is not None and rect.collidepoint(puntero):
                    self.equipar((grupo,nivel), diario)
                    puesta = True
                papel(pantalla, rect, (209,225,191) if puesta else (238,225,194) if ganada else (225,218,197))
                escribir(pantalla,nombre_prenda,(rect.centerx,rect.top+24),17,ancho=164,negrita=ganada)
                estado = 'Puesta' if puesta else 'Equipar' if ganada else f'Premio de nivel {nivel + 1}'
                escribir(pantalla,estado,(rect.centerx,rect.top+50),16,MUSGO)
        escribir(pantalla,'Completá niveles para sumar prendas al armario',(480,590),20)

    def dibujar(self, pantalla, puntero, activar, ahora, diario):
        """Presenta cuatro acciones de cuidado con respuesta visual."""
        if self.armario:
            self.dibujar_armario(pantalla,puntero,activar,ahora,diario)
            return
        if activar and puntero is not None:
            if ABRIR_ARMARIO.collidepoint(puntero):
                self.armario = True
                return
            for indice, rect in enumerate(BOTONES):
                if rect.collidepoint(puntero):
                    self.cuidar(CUIDADOS[indice], ahora)
                    break
            else:
                if MASCOTA.collidepoint(puntero):
                    self.cuidar('Caricias', ahora)
        papel(pantalla, (53,40,854,600))
        escribir(pantalla,'La casa de tu compañero',(416,96),36,titulo=True,ancho=490)
        boton(pantalla, ABRIR_ARMARIO, 'Armario')
        escribir(pantalla,self.mensaje,(480,152),22,ancho=720)
        pygame.draw.ellipse(pantalla,(192,179,129),(376,360,208,29))
        activo = ahora < self.hasta
        salto = 18 * abs(math.sin(ahora * 10)) if activo and self.accion == 'Juego' else 0
        dibujar_familiar(pantalla,(480,305-salto),activo and self.accion == 'Comida',ahora,prenda=self.prenda)
        if activo:
            color = (116,185,193) if self.accion == 'Baño' else (218,151,123)
            for indice in range(6):
                fase = ahora * 1.9 + indice * math.tau/6
                x, y = 480 + math.cos(fase)*80, 300 + math.sin(fase)*63
                pygame.draw.circle(pantalla,color,(round(x),round(y)),4 + indice%3,2)
        escribir(pantalla,'Hacé pinza sobre él para acariciarlo',(480,436),21,MUSGO)
        for accion, rect in zip(CUIDADOS, BOTONES):
            boton(pantalla,rect,accion,puntero is not None and rect.collidepoint(puntero))
            escribir(pantalla,f'{self.cuidados[accion]} veces',
                     (rect.centerx, 602),17,TINTA)
